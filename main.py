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
from gacha import *

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
        profile_display = ProfileDisplay(user_id=interaction.user.id, discord_user=interaction.user)
        await profile_display.send_profile(interaction)
    
    @discord.ui.button(label="Show Inventory 📦", style=discord.ButtonStyle.primary, row=0)
    async def show_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @bot.command(name="leaderboard")
    async def leaderboard(ctx):
        top_users = User.objects().order_by('-level', '-exp')[:10]
        
        if not top_users:
            return

        embed = discord.Embed(
            title="Leaderboard - Top 10 Users by Level",
            color=discord.Color.gold()
        )

        for index, user in enumerate(top_users, 1):
            embed.add_field(
                name=f"#{index} - {user.user_name}",
                value=f"Level: {user.level}, EXP: {user.exp}",
                inline=False
            )

        await ctx.send(embed=embed)


class ProfileDisplay(discord.ui.View):
    def __init__(self, user_id, discord_user):
        super().__init__(timeout=None)  
        self.user_id = user_id
        self.discord_user = discord_user

    async def send_profile(self, interaction: discord.Interaction):

        user = User.objects(discord_id=str(self.user_id)).first()
        if user:
            embed = discord.Embed(
                                title="User Profile",
                                description=f"**User Name:** {user.user_name}\n"
                                            f"**Level:** {user.level}\n"
                                            f"**Exp:** {user.exp}\n",
                                color=discord.Color.darker_gray())

            embed.set_thumbnail(url=self.discord_user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            print("User Not Found")


# Dictionary to store user join times
user_voice_time = {}

INTERVAL_MINUTES = 0.5  # Adjust as necessary

@bot.event
async def on_voice_state_update(member, before, after):
    # User joins a voice channel
    if before.channel is None and after.channel is not None:
        if member.id not in user_voice_time:
            user_voice_time[member.id] = {"join_time": datetime.now(), "total_time": timedelta(0), "gacha": 0}
        else:
            user_voice_time[member.id]["join_time"] = datetime.now()

        print(f"{member.name} joined voice channel {after.channel.name} at {user_voice_time[member.id]['join_time']}")
    
    # User leaves the voice channel
    elif before.channel is not None and after.channel is None:
        join_time = user_voice_time[member.id].get("join_time")
        if join_time:
            time_spent = datetime.now() - join_time
            user_voice_time[member.id]["total_time"] += time_spent

            total_minutes = user_voice_time[member.id]["total_time"].total_seconds() / 60
            print(f"{member.name} has spent {total_minutes:.2f} minutes in the voice channel.")

            user_voice_time[member.id]["join_time"] = None


@tasks.loop(minutes=1.0)  # Run every x minute
async def track_gacha_points():
    print("Tracking gacha points...")
    
    for member_id, data in list(user_voice_time.items()):
        join_time = data.get("join_time")
        if join_time:
            # Calculate time spent in the current session
            time_spent = datetime.now() - join_time
            total_minutes = time_spent.total_seconds() / 60
            
            print(f"Member {member_id} total minutes: {total_minutes}")

            if total_minutes >= INTERVAL_MINUTES:
                # Find the user in MongoDB
                user = User.objects(discord_id=str(member_id)).first()
                
                if user:
                    # Increment gacha roll count and save
                    user.roll_count += 1
                    user.save()

                    # Increment local gacha counter
                    data["gacha"] += 1

                    # Reset join_time to now for the next interval
                    data["join_time"] = datetime.now()

                    print(f"{user.user_name} earned 1 gacha point. Now has {user.roll_count} gacha points.")
                else:
                    print(f"User with ID {member_id} not found in database.")

@bot.command(name="create_users")
@commands.has_permissions(administrator=True)  # Only allow administrators to use this command
async def create_users(ctx):
    guild = ctx.guild  # Get the server (guild) where the command is executed
    
    # Iterate over all members of the server
    for member in guild.members:
        # Check if the member already has a User object in the MongoDB
        try:
            User.objects.get(discord_id=str(member.id))
            print(f"User {member.name} already exists.")
        except DoesNotExist:
            # If user doesn't exist, create a new User document
            new_user = User(
                discord_id=str(member.id),
                user_name=member.name  # You can use `member.display_name` if you prefer the display name
            )
            new_user.save()
            print(f"Created new user for {member.name}.")

    await ctx.send("User creation process completed!")

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    channel_id = 1047103852131930142
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
                
                await channel.send(embed=embed, file=image_file, view=ShowProfile())
        else:
            embed = discord.Embed(
                title="Techhub's Mainmenu", 
                description="Select an option to proceed."
            )
        
            await channel.send(embed=embed, view=ShowProfile())
            if not track_gacha_points.is_running():
                track_gacha_points.start()

    else:
        print(f"Channel with ID {channel_id} not found.")

    gacha_id = 1293603902419243058
    gacha_channel = bot.get_channel(gacha_id)

    embed = discord.Embed(
                title="Techhub's Gacha"
            )
    await gacha_channel.send(embed=embed, view=GachaView())

bot.run(BOT_TOKEN)
