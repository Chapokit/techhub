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

class TradeFragments(discord.ui.Select):
    def __init__(self, user_inventory):

        options = []
        for item, value in user_inventory.items():
            # Skip "HCoin" from being included in the dropdown
            if item == "HCoin":
                continue

            # Set trade_value based on the item
            if item == "Big Enter":
                trade_value = 3
                item = f"⏎ {item}"
            elif item == "JBL":
                trade_value = 3
                item = f"🎧 {item}"
            elif item == "Rimuru":
                trade_value = 4
                item = f"🧢 {item}"
            elif item == "Divoom":
                trade_value = 5
                item = f"🖥️ {item}"
            elif item == "Mechanical":
                trade_value = 5
                item = f"⚙️ {item}"
            else:
                trade_value = 1  # Set a default trade_value for any other items


            if value > 0: 
                options.append(discord.SelectOption(label=f"{item}", description=f"Your Amount: {value}/[Trade Value: {trade_value}]"))

        # Call the parent constructor with the options
        super().__init__(placeholder="Select an item to combine...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Handle the user's selection here (e.g., combining fragments or further actions)
        selected_item = self.values[0]  # Get the selected item
        await interaction.response.send_message(f"You selected to combine: {selected_item}")

class TradeFragmentsView(discord.ui.View):
    def __init__(self, user_inventory):
        super().__init__()
        # Add the TradeFragments dropdown to this view
        self.add_item(TradeFragments(user_inventory))

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Combine Fragments", style=discord.ButtonStyle.primary)
    async def combine_fragments(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get the user from the database
        user = User.objects(discord_id=str(interaction.user.id)).first()

        if not user:
            await interaction.response.send_message("User not found.", ephemeral=True)
            return

        # Create a view with the dropdown based on the user's inventory
        view = TradeFragmentsView(user.inventory)

        # Send the view with the dropdown to the user
        await interaction.response.send_message("Select an item to combine:", view=view, ephemeral=True)

# Assuming bot is defined elsewhere in your project