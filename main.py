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

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class ShowMenu(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Show Profile 📝", style=discord.ButtonStyle.primary, row=0)
    async def show_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create an instance of the ProfileDisplay class and call its display_profile method
        profile_display = ProfileDisplay(user_id=interaction.user.id, discord_user=interaction.user)
        await profile_display.send_profile(interaction)
    
    @discord.ui.button(label="Show Inventory 📦", style=discord.ButtonStyle.primary, row=0)
    async def show_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = User.objects(discord_id=str(interaction.user.id)).first()  # Retrieve the user from the database

        if user:
            # Create an embed to display the user's inventory
            embed = discord.Embed(title=f"{user.user_name}'s Inventory", color=discord.Color.blue())

            embed.add_field(name="Level", value=f"`{user.level}`", inline=True)

            # Calculate experience needed for the next level
            exp_needed = exp_needed_for_level(user.level)

            # Create the progress bar based on a percentage
            if exp_needed > 0:  # Prevent division by zero
                percentage = min(100, (user.exp / exp_needed) * 100)  # Calculate the percentage, capped at 100%
                filled_length = int(10 * (percentage / 100))  # Calculate how much of the bar is filled (max 10 blocks)
            else:
                filled_length = 0

            unfilled_length = 10 - filled_length  # Calculate the unfilled length

            # Construct the progress bar
            bar = "🟩" * filled_length + "⬜" * unfilled_length  # Green for current exp, gray for needed exp

            # Add experience field with progress bar and current/needed experience
            embed.add_field(name="Experience", value=f"{bar}  (*{percentage:.1f}%*)", inline=True)
            embed.add_field(name="Hamster Coin 🪙", value=f"`{user.inventory['HCoin']}`", inline=False)

            inventory_items = {
                'Big Enter': ['⏎', 3], 
                'JBL': ['🎧', 3], 
                'Rimuru': ['🧢', 4],
                'Divoom': ['🖥️', 5], 
                'Mechanical': ['⚙️', 5]
            }

            # Create a list to store formatted inventory display
            inventory_rows = []
            current_row = []

            for item, (emoji, max_value) in inventory_items.items():
                # Get the count of the item from the user's inventory, default to 0 if not found
                value = user.inventory.get(item, 0) 
                if value == 0:
                    pass
                else:
                    # Add formatted item with emoji, name, and count
                    current_row.append(f"{emoji} `{item}`: `{value}/{max_value}`") 

                if len(current_row) == 3:  # If we have 4 items in the current row, join and reset
                    inventory_rows.append(" | ".join(current_row))  # Join with a separator
                    current_row = []

            # Add any remaining items in the current row
            if current_row:
                inventory_rows.append(" | ".join(current_row))

            if not inventory_rows:
                inventory_display = "There are currently no fragments in your collection."
            else:
                inventory_display = "\n".join(inventory_rows)

            # Add the inventory display to the embed
            embed.add_field(
                name="Inventory",
                value=inventory_display,  # Join all rows into a single string
                inline=False  # Ensure it doesn't try to align it horizontally with other fields
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)  # Send the embed message
        else:
            await interaction.response.send_message("User not found.", ephemeral=True)

    @discord.ui.button(label="Search Profile 🔎", style=discord.ButtonStyle.primary, row=1)
    async def search_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create and show the modal for searching by ID or name
        await interaction.response.send_modal(SearchProfileModal())

    @discord.ui.button(label="แลกของรางวัล 🎁", style=discord.ButtonStyle.primary, row=1)
    async def combine_fragments(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get the user from the database
        user = User.objects(discord_id=str(interaction.user.id)).first()

        if not user:
            await interaction.response.send_message("User not found.", ephemeral=True)
            return

        # Create a view with the dropdown based on the user's inventory
        view = TradeFragmentsView(user.inventory, user)

        # Send the view with the dropdown to the user
        await interaction.response.send_message("Select an item to combine: (ต้องมีชิ้นส่วนครบตามกำหนดถึงจะแลกได้):", view=view, ephemeral=True)


class ProfileDisplay(discord.ui.View):
    def __init__(self, user_id, discord_user):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.discord_user = discord_user

    async def send_profile(self, interaction: discord.Interaction):
        user = User.objects(discord_id=str(self.user_id)).first()
        if user:
            # Calculate experience needed for the next level
            exp_needed = exp_needed_for_level(user.level)

            # Create the progress bar based on a percentage
            if exp_needed > 0:  # Prevent division by zero
                percentage = min(100, (user.exp / exp_needed) * 100)  # Calculate the percentage, capped at 100%
                filled_length = int(10 * (percentage / 100))  # Calculate how much of the bar is filled (max 10 blocks)
            else:
                filled_length = 0

            unfilled_length = 10 - filled_length  # Calculate the unfilled length

            # Construct the progress bar
            bar = "🟩" * filled_length + "⬜" * unfilled_length  # Green for current exp, gray for needed exp

            # Create the embed with the progress bar
            embed = discord.Embed(
                title="User Profile",
                description=f"User Name: `{user.user_name}`\n"
                            f"Level: `{user.level}`\n"
                            f"Exp: `{user.exp}` / `{exp_needed:.0f}`\n"
                            f"Progress: {bar} (*{percentage:.1f}%*)",
                color=discord.Color.darker_gray()
            )

            embed.set_thumbnail(url=self.discord_user.avatar.url)  # Set avatar as thumbnail
            await interaction.response.send_message(embed=embed, ephemeral=True)  # Send the profile embed
        else:
            print("User Not Found")

class SearchProfileModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Search User Profile", custom_id="search_profile_modal")


        self.search_query = discord.ui.TextInput(
            label="Enter Discord ID or Name",
            placeholder="Search by ID or name",
            required=True
        )
        self.add_item(self.search_query)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.search_query.value
        # Search for user by discord_id or user_name
        user = User.objects(discord_id=query).first() or User.objects(user_name=query).first()

        if user:
            # Instantiate the ProfileDisplay class and call send_profile
            profile_view = ProfileDisplay(user_id=user.discord_id, discord_user=interaction.user)
            await profile_view.send_profile(interaction)
        else:
            await interaction.response.send_message("User not found. Please try again.", ephemeral=True)

# Dictionary to store user join times
user_voice_time = {}

INTERVAL_MINUTES = 120  # Adjust as necessary

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


@tasks.loop(minutes=122.0)  # Run every x minute
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

@bot.event
async def on_member_join(member):
    # Check if the user already exists in the database
    try:
        User.objects.get(discord_id=str(member.id))
        print(f"User {member.name} already exists.")
    except DoesNotExist:
        # If the user does not exist, create a new User document
        new_user = User(
            discord_id=str(member.id),
            user_name=member.name  # Or use member.display_name for display names
        )
        new_user.save()
        print(f"Created new user for {member.name}.")

    # You can send a welcome message if you want
    channel = member.guild.system_channel  # Or specify a different channel
    if channel is not None:
        await channel.send(f"Welcome {member.mention}! Your user profile has been created.")

    try:
        await member.send(f"Hey {member.name}, welcome to the server! If you have any questions, feel free to ask.")
    except discord.Forbidden:
        print(f"Could not send a DM to {member.name}.")

for command in commands_list:
    bot.add_command(command)

@bot.event
async def on_ready():

    print(f'Logged on as {bot.user}!')
    channel_id = 1295940243610144808
    channel = bot.get_channel(channel_id)

    if channel is not None:
        image_path = 'picture/grey.png'
        
        if os.path.isfile(image_path):
            embed = discord.Embed(
                title="Techhub's Mainmenu", 
                description="Select an option to proceed."
            )
            
            with open(image_path, 'rb') as file:
                image_file = discord.File(file, os.path.basename(image_path))
                embed.set_image(url=f"attachment://{os.path.basename(image_path)}")
                
                await channel.send(embed=embed, file=image_file, view=ShowMenu())
        else:
            embed = discord.Embed(
                title="Techhub's Mainmenu", 
                description="Select an option to proceed."
            )
        
            await channel.send(embed=embed, view=ShowMenu())
            if not track_gacha_points.is_running():
                track_gacha_points.start()

    else:
        print(f"Channel with ID {channel_id} not found.")








bot.run(BOT_TOKEN)
