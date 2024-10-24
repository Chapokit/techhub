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
    def __init__(self, user_inventory, user):
        self.user = user

        options = []
        for item, value in user_inventory.items():
            # Skip "HCoin" from being included in the dropdown
            if item == "HCoin":
                continue

            # Set trade_value based on the item
            if item == "Big Enter":
                trade_value = 3
                display_name = f"⏎ {item}"
            elif item == "JBL":
                trade_value = 3
                display_name = f"🎧 {item}"
            elif item == "Rimuru":
                trade_value = 4
                display_name = f"🧢 {item}"
            elif item == "Divoom":
                trade_value = 5
                display_name = f"🖥️ {item}"
            elif item == "Mechanical":
                trade_value = 5
                display_name = f"⚙️ {item}"
            else:
                trade_value = 1  # Set a default trade_value for any other items
                display_name = item

            # Only add options for items that have more than 0 quantity
            if value > 0:
                # Use the full item name (with emoji) as the label but store the item name as value
                options.append(discord.SelectOption(label=display_name, description=f"Your Amount: {value}/[Trade Value: {trade_value}]", value=item))

        # Call the parent constructor with the options
        super().__init__(placeholder="Select an item to combine...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Get the selected item (the value is the full item name without emoji)
        selected_item = self.values[0]

        # Set the trade value for the selected item
        trade_values = {
            "Big Enter": 3,
            "JBL": 3,
            "Rimuru": 4,
            "Divoom": 5,
            "Mechanical": 5
        }

        trade_value = trade_values.get(selected_item, 1)  # Default trade value is 1 if not listed

        # Check if the user has enough of the selected item to trade
        if self.user.inventory[selected_item] < trade_value:
            await interaction.response.send_message(f"You don't have enough fragments to trade for: {selected_item} [`need {trade_value}`]")
        else:
            # Deduct the required amount from inventory and add to traded items
            self.user.inventory[selected_item] -= trade_value
            self.user.traded_items.append(selected_item)
            self.user.save()

            await interaction.response.send_message(f"Successfully traded for: {selected_item}", ephemeral=True)


class TradeFragmentsView(discord.ui.View):
    def __init__(self, user_inventory, user):
        super().__init__()
        # Add the TradeFragments dropdown to this view
        self.add_item(TradeFragments(user_inventory, user))

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
        view = TradeFragmentsView(user.inventory, user)

        # Send the view with the dropdown to the user
        await interaction.response.send_message("Select an item to combine:", view=view, ephemeral=True)

# Assuming bot is defined elsewhere in your project