from typing import List
import discord
import asyncio

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

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__()

    async def countdown(self, interaction):
        # Send a message indicating the countdown
        countdown_message = await interaction.followup.send("Rolling in 3...", ephemeral=True)
        await asyncio.sleep(1)
        await interaction.followup.send("Rolling in 2...", ephemeral=True)
        await asyncio.sleep(1)
        await interaction.followup.send("Rolling in 1...", ephemeral=True)
        await asyncio.sleep(1)

        # Now we can roll the gacha
        await interaction.followup.send("Rolling...", ephemeral=True)

    async def send_gacha_results(self, interaction, results):
        embed = discord.Embed(title="Gacha Results", description="You got:")
        for result in results:
            embed.add_field(name=result, value=" ", inline=False)

        # Send the embed message
        gacha_message = await interaction.followup.send(embed=embed, ephemeral=True)

        # Wait for 60 seconds before deleting the message
        await asyncio.sleep(60)
        await gacha_message.delete()

    @discord.ui.button(label="Roll Gacha x1", style=discord.ButtonStyle.primary, row=0)
    async def one_roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.countdown(interaction)

        result = roll_gacha(interaction.user.id)  # Call the gacha function
        await self.send_gacha_results(interaction, [result])

    @discord.ui.button(label="Roll Gacha x10", style=discord.ButtonStyle.primary, row=0)
    async def ten_rolls(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.countdown(interaction)

        results = []
        for _ in range(10):
            result = roll_gacha(interaction.user.id)  # Call the gacha function
            results.append(result)

        await self.send_gacha_results(interaction, results)

    @discord.ui.button(label="Check Gacha Rate", style=discord.ButtonStyle.primary, row=0)
    async def show_rate(self, interaction: discord.Interaction, button: discord.ui.Button):
        gacha_rate = check_rate(user_id=interaction.user.id)
        
        embed = discord.Embed(
            title="*****GACHA RATE******",
            description=f"**User Name:** {interaction.user.name}\n**Gacha Rate:** {gacha_rate} %",
            color=discord.Color.darker_gray()
        )
        
        await interaction.response.send_message(embed=embed)

class GachaResult(discord.ui.View):
    def __init__(self, user_id, discord_user):
        super().__init__()
        self.user_id = user_id
        self.discord_user = discord_user

    async def display_result(self, interaction: discord.Interaction):
        result = roll_gacha(self.user_id)
        await interaction.followup.send(result, ephemeral = True)  # Send the actual result after processing
