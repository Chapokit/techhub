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

    @discord.ui.button(label="Roll Gacha x1", style=discord.ButtonStyle.primary, row=0)
    async def one_roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        gacha_result = GachaResult(user_id=interaction.user.id, discord_user=interaction.user)
        await interaction.response.send_message("You got : ")
        await gacha_result.display_result(interaction)

    @discord.ui.button(label="Roll Gacha x10", style=discord.ButtonStyle.primary, row=0)
    async def ten_rolls(self, interaction: discord.Interaction, button: discord.ui.Button):
        gacha_result = GachaResult(user_id=interaction.user.id, discord_user=interaction.user)
        await interaction.response.send_message("You got : ")
        for _ in range(10):
            await gacha_result.display_result(interaction)

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
        await interaction.followup.send(result)
