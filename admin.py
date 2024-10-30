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
from user_commands import commands_list

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
MONGODB_URI = str(os.getenv("MONGODB_URI"))

client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

print("Current Working Directory:", os.getcwd())

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.presences = True 
intents.message_content = True  
intents.guilds = True   

class Quest_Modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Create Forum Quest",)

class AdminMenu(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="สร้าง Quest 📝", style=discord.ButtonStyle.primary, row=0)
    async def create_quest(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("User not found. Please try again.", ephemeral=True)


