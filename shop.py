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

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Combine Fragments", style=discord.ButtonStyle.primary)
    async def combine_fragments(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass