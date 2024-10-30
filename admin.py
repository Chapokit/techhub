import discord
from discord.ext import tasks, commands

from discord.ui import View, Button, Modal, TextInput, Select
import asyncio

from leader_board import*

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine.errors import DoesNotExist

from classes import *
from functions import *
from gacha import *
from shop import *

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
MONGODB_URI = str(os.getenv("MONGODB_URI"))

client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))


intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.presences = True 
intents.message_content = True  
intents.guilds = True   

class QuestModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Create Forum Quest")

        self.quest_name = discord.ui.TextInput(
            label="Quest Name",
            placeholder="Enter the quest name...",
            max_length=100
        )
        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Enter the quest description...",
            style=discord.TextStyle.paragraph  # Multi-line input
        )
        self.reward = discord.ui.TextInput(
            label="Reward",
            placeholder="Enter the quest reward... (Ex. 150 Exp, 20 Hamster Coins)",
            max_length=100
        )
        self.due_date = discord.ui.TextInput(
            label="Due Date",
            placeholder="Enter the due date (e.g., YYYY-MM-DD)...",
            max_length=20
        )

        # Add inputs to the modal
        self.add_item(self.quest_name)
        self.add_item(self.description)
        self.add_item(self.reward)
        self.add_item(self.due_date)

    async def on_submit(self, interaction: discord.Interaction):
        # Store the collected info in the view so it can be used in the dropdown step
        view = DifficultyDropdown(
            quest_name=self.quest_name.value,
            description=self.description.value,
            reward=self.reward.value,
            due_date=self.due_date.value
        )
        # Send the dropdown menu for selecting difficulty
        await interaction.response.send_message("Select the difficulty for this quest:", view=view, ephemeral=True)

class DifficultyDropdown(discord.ui.View):
    def __init__(self, quest_name, description, reward, due_date):
        super().__init__()
        self.quest_name = quest_name
        self.description = description
        self.reward = reward
        self.due_date = due_date

        # Dropdown for difficulty selection
        self.add_item(DifficultySelect(self))

class DifficultySelect(discord.ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view  # Store the parent view to access the quest info
        options = [
            discord.SelectOption(label="Easy", description="Low difficulty"),
            discord.SelectOption(label="Medium", description="Moderate difficulty"),
            discord.SelectOption(label="Hard", description="High difficulty")
        ]
        super().__init__(placeholder="Choose the difficulty level", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        difficulty = self.values[0]

        forum_channel_id = 1301121119855841280
        forum_channel = interaction.guild.get_channel(forum_channel_id)

        thread = await forum_channel.create_thread(
            name=f"{self.parent_view.quest_name} ({difficulty})",
            content=(
                f"**Quest Details**:\n{self.parent_view.description}\n"
                f"\n**Due Date** \n- {self.parent_view.due_date}"
                f"\n**Reward** \n- {self.parent_view.reward}\n"
            ),
        )

        await interaction.response.send_message(f"Thread created for quest: {self.parent_view.quest_name} with difficulty: {difficulty}", ephemeral=True)

class AdminMenu(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Create Quest 📝", style=discord.ButtonStyle.primary, row=0)
    async def create_quest(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show the QuestModal to collect quest info
        await interaction.response.send_modal(QuestModal())

    @discord.ui.button(label="Create All Users 👦", style=discord.ButtonStyle.primary, row=0)
    async def create_all_users(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild  # Get the guild from the interaction
        count = 0

        for member in guild.members:
            if not member.bot:  # Skip bots
                # Check if user already exists in the database
                existing_user = User.objects(discord_id=str(member.id)).first()

                if existing_user is None:
                    # Create new User document if not exists
                    new_user = User(
                        discord_id=str(member.id),
                        user_name=member.name
                    )
                    new_user.save()
                    count += 1  # Track how many users were created
                    print(f"Created {member.name}")
                    
                    # Add a slight delay between user creations (e.g., 0.1 seconds)
                    await asyncio.sleep(0.1)

        # Respond to the interaction once all users are created
        await interaction.followup.send(f"Created {count} new User objects for members in the server!", ephemeral=True)



