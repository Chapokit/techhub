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

class Leaderboard:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id
        self.message = None  # To keep track of the leaderboard message in the channel

    async def update_leaderboard(self):
        """Fetch the top 10 users by level and roll_all_time and update the message in the leaderboard channel."""
        # Fetch top 10 users, first by level, then by roll_all_time
        top_users = User.objects().order_by('-level', '-roll_all_time')[:10]
        
        if not top_users:
            return "No users found in the leaderboard."

        embed = discord.Embed(
            title="Leaderboard - Top 10 Users by Level and Gacha Rolls",
            color=discord.Color.gold()
        )

        for index, user in enumerate(top_users, 1):
            embed.add_field(
                name=f"#{index} - {user.user_name}",
                value=f"Level: {user.level}, EXP: {user.exp}, Total Rolls: {user.roll_all_time}",
                inline=False
            )

        channel = self.bot.get_channel(self.channel_id)
        if channel is not None:
            # Update the message or send a new one
            if self.message is None:
                self.message = await channel.send(embed=embed)
            else:
                await self.message.edit(embed=embed)  # Edit the existing message to update it

    @tasks.loop(minutes=5.0)  # Set the interval for leaderboard updates (e.g., every 5 minutes)
    async def start_leaderboard_updates(self):
        """Periodically update the leaderboard."""
        await self.update_leaderboard()

    @start_leaderboard_updates.before_loop
    async def before_updates(self):
        """Wait for the bot to be fully ready before starting the loop."""
        await self.bot.wait_until_ready()
