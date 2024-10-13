import discord
from discord.ext import tasks, commands

from discord.ui import View, Button, Modal, TextInput, Select
import asyncio

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from classes import *
from functions import *

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

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

class ShowProfile(discord.ui.View):
    def __init__(self):
        super().__init__()

        @discord.ui.button(label="Show Profile 📝", style=discord.ButtonStyle.primary, row=0)
        async def show_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Create an instance of the ProfileDisplay class and call its display_profile method
            profile_display = ProfileDisplay(user_id=interaction.user.id)
            await profile_display.send_profile(interaction)

class ProfileDisplay(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)  
        self.user_id = user_id

    async def send_profile(self, interaction: discord.Interaction):

        # user = User.objects(discord_id=str(self.user_id)).first()
        user = None
        if user:
            embed = discord.Embed(title=""
                                  ,description=""
                                  ,color=discord.Color.darker_gray)
            embed.set_thumbnail(url=self.discord_user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            print("User Not Found")



@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    channel_id = 1292785692694544415
    channel = bot.get_channel(channel_id)

    if channel is not None:
        image_path = 'path_to_image.png'
        
        if os.path.isfile(image_path):
            embed = discord.Embed(
                title="Techhub's Mainmenu", 
                description="Select an option to proceed."
            )
            
            with open(image_path, 'rb') as file:
                image_file = discord.File(file, os.path.basename(image_path))
                embed.set_image(url=f"attachment://{os.path.basename(image_path)}")
                
                await channel.send(embed=embed, file=image_file)
                await channel.send(view=ShowProfile())
        else:
            embed = discord.Embed(
                title="Techhub's Mainmenu", 
                description="Select an option to proceed."
            )
        
            await channel.send(embed=embed)
            await channel.send(view=ShowProfile())
    else:
        print(f"Channel with ID {channel_id} not found.")

# Dictionary to store user join times
user_voice_time = {}

@bot.event
async def on_voice_state_update(member, before, after):
    voice_channel = bot.get_channel(1292785692694544415)
    
    # User joins a voice channel
    if before.channel is None and after.channel is not None:
        # Log the join time and total accumulated time
        if member.id not in user_voice_time:
            user_voice_time[member.id] = {"join_time": datetime.now(), "total_time": timedelta(0)}
        else:
            user_voice_time[member.id]["join_time"] = datetime.now()
        
        print(f"{member.name} joined voice channel {after.channel.name} at {user_voice_time[member.id]['join_time']}")
    
    # User leaves the voice channel
    elif before.channel is not None and after.channel is None:
        # Calculate the time spent in the voice channel during this session
        join_time = user_voice_time[member.id].get("join_time")
        
        if join_time is not None:
            time_spent = datetime.now() - join_time
            user_voice_time[member.id]["total_time"] += time_spent  # Add to total time

            total_hours = user_voice_time[member.id]["total_time"].total_seconds() / 3600
            print(f"{member.name} has spent {total_hours:.2f} hours in the voice channel.")

            # Check how many complete 2-hour intervals have passed and notify accordingly
            intervals = int(total_hours // 2)  
            for i in range(1, intervals + 1):
                print(f"{member.name} has spent {i * 2} hours in the voice channel.")
                

            user_voice_time[member.id]["join_time"] = None

@bot.event
async def on_disconnect():
    # Clear tracking data on bot disconnect
    user_voice_time.clear()

bot.run(BOT_TOKEN)