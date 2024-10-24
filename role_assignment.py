from typing import List
import discord
import asyncio
from discord.ext import tasks, commands

from discord.utils import MISSING
from dotenv import load_dotenv
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from classes import *
from functions import *

load_dotenv()

MONGODB_URI = str(os.getenv("MONGODB_URI"))
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.presences = True
intents.message_content = True

class FirstCategorySelect(discord.ui.View):
    def __init__(self, artist_role_id, programmer_role_id, gamedev_role_id, other_role_id):
        super().__init__()
        self.artist_role_id = artist_role_id
        self.programmer_role_id = programmer_role_id
        self.gamedev_role_id = gamedev_role_id
        self.other_role_id = other_role_id

    # Artist button with emoji 🎨 in label
    @discord.ui.button(label="🎨 Artist", style=discord.ButtonStyle.primary)
    async def artist_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, self.artist_role_id, "Artist")

    # Programmer button with emoji 💻 in label
    @discord.ui.button(label="💻 Programmer", style=discord.ButtonStyle.primary)
    async def programmer_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, self.programmer_role_id, "Programmer")

    # Game Developer button with emoji 🎮 in label
    @discord.ui.button(label="🎮 Game Dev", style=discord.ButtonStyle.primary)
    async def gamedev_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, self.gamedev_role_id, "Game Dev")

    # Other button with emoji 🛠️ in label
    @discord.ui.button(label="🛠️ Other", style=discord.ButtonStyle.primary)
    async def other_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, self.other_role_id, "Other")

    async def toggle_role(self, interaction: discord.Interaction, role_id: int, role_name: str):
        guild = interaction.guild  # Access the guild from the interaction object

        if guild is None:
            await interaction.response.send_message(f"Could not retrieve the guild. Make sure the bot has access to the server.", ephemeral=True)
            return

        role = guild.get_role(role_id)  # Get the role using the role ID

        if role:
            # Get the user who clicked the button
            user = interaction.user

            # Add or remove role
            if role in user.roles:
                await user.remove_roles(role)
                await interaction.response.send_message(f"Removed '{role_name}' role!", ephemeral=True)
            else:
                await user.add_roles(role)
                await interaction.response.send_message(f"Granted '{role_name}' role!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Role '{role_name}' not found.", ephemeral=True)

class SecondCategorySelect(discord.ui.View):
    def __init__(self, roles_mapping):
        super().__init__()
        self.roles_mapping = roles_mapping

    # Buttons with specific roles and their corresponding emojis in labels
    @discord.ui.button(label="🖼️ 3D Artist", style=discord.ButtonStyle.primary)
    async def artist_3d_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "3D Artist")

    @discord.ui.button(label="🎨 2D Artist", style=discord.ButtonStyle.primary)
    async def artist_2d_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "2D Artist")

    @discord.ui.button(label="🎥 Animator", style=discord.ButtonStyle.primary)
    async def animator_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "Animator")

    @discord.ui.button(label="🎼 Music Composer", style=discord.ButtonStyle.primary)
    async def music_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "Music Composer")

    @discord.ui.button(label="🕹️ Unity Dev", style=discord.ButtonStyle.primary)
    async def unity_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "Unity Dev")

    @discord.ui.button(label="🎮 Unreal Dev", style=discord.ButtonStyle.primary)
    async def unreal_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "Unreal Dev")

    @discord.ui.button(label="🧱 Roblox Dev", style=discord.ButtonStyle.primary)
    async def roblox_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "Roblox Dev")

    @discord.ui.button(label="📜 C# Dev", style=discord.ButtonStyle.primary)
    async def csharp_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "C# Dev")

    @discord.ui.button(label="🐍 Python Dev", style=discord.ButtonStyle.primary)
    async def python_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.toggle_role(interaction, "Python Dev")

    async def toggle_role(self, interaction, role_name):
        role_id = self.roles_mapping.get(role_name)
        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message(f"Removed '{role_name}' role!", ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"Granted '{role_name}' role!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Role '{role_name}' not found.", ephemeral=True)
