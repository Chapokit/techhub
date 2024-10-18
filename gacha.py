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


class PrizeView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    @discord.ui.button(label="Claim Prize 🎁", style=discord.ButtonStyle.success)
    async def claim_prize(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = User.objects(discord_id=str(self.user_id)).first()
        
        if user:
            # Check if the user has at least one of each fragment
            if (user.fragment['fragment1'] >= 1 and
                user.fragment['fragment2'] >= 1 and
                user.fragment['fragment3'] >= 1):
                
                # Deduct one from each fragment
                user.fragment['fragment1'] -= 1
                user.fragment['fragment2'] -= 1
                user.fragment['fragment3'] -= 1
                
                user.inventory.append("Mystery Prize")  # Assuming you have an inventory field
                user.save()
                
                await interaction.response.send_message("You have claimed your prize! 🎉", ephemeral=True)
            else:
                await interaction.response.send_message("You need at least one of each fragment to claim this prize.", ephemeral=True)
        else:
            await interaction.response.send_message("User not found.", ephemeral=True)


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

    @discord.ui.button(label="Roll Gacha x1 🎰", style=discord.ButtonStyle.primary, row=0)
    async def one_roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        user = User.objects(discord_id=str(interaction.user.id)).first()
        if user.roll_count > 0:
            user.roll_count -= 1
            user.roll_all_time += 1
            user.save()

            await interaction.response.defer()
            await self.countdown(interaction)

            result = roll_gacha(interaction.user.id)  # Call the gacha function
            await self.send_gacha_results(interaction, [result])
        
        else:
            await interaction.response.send_message(f"You don't have enough gacha points. {user.roll_count} rolls left.", ephemeral=True)


    @discord.ui.button(label="Roll Gacha x10 🎰", style=discord.ButtonStyle.primary, row=0)
    async def ten_rolls(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = User.objects(discord_id=str(interaction.user.id)).first()
        if user.roll_count > 10:
            user.roll_count -= 10
            user.roll_all_time += 10
            user.save()

            await interaction.response.defer()
            await self.countdown(interaction)

            results = []
            for _ in range(10):
                result = roll_gacha(interaction.user.id)  # Call the gacha function
                results.append(result)

            await self.send_gacha_results(interaction, results)

        else:
            await interaction.response.send_message(f"You don't have enough gacha points. {user.roll_count} rolls left.", ephemeral=True)

    @discord.ui.button(label="Check Gacha Rate %", style=discord.ButtonStyle.primary, row=1)
    async def show_rate(self, interaction: discord.Interaction, button: discord.ui.Button):
        gacha_rate = check_rate(user_id=interaction.user.id)
        
        embed = discord.Embed(
            title="*****GACHA RATE******",
            description=f"**User Name:** {interaction.user.name}\n**Gacha Rate:** {gacha_rate} %\n Your gacha rates depend on your level",
            color=discord.Color.darker_gray()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Buy Prizes 🎁", style=discord.ButtonStyle.success, row=1)
    async def buy_prize(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create the embed for the prize requirements
        embed = discord.Embed(
            title="Prize Purchase",
            description="To claim your prize, you need the following:",
            color=discord.Color.green()
        )
        
        # Add fields for required information (customize as needed)
        embed.add_field(name="Requirement 1", value="1000 coins", inline=False)
        embed.add_field(name="Requirement 2", value="Level 5 or above", inline=False)
        embed.add_field(name="Requirement 3", value="1 Gacha Roll", inline=False)

        # Create a PrizeView for the user
        prize_view = PrizeView(user_id=interaction.user.id)

        # Send both the embed and the button in the same message
        await interaction.response.send_message(
            "Click the button below to claim your prize.",
            embed=embed,
            view=prize_view,
            ephemeral=True  # Make the message visible only to the user
        )

class GachaResult(discord.ui.View):
    def __init__(self, user_id, discord_user):
        super().__init__()
        self.user_id = user_id
        self.discord_user = discord_user

    async def display_result(self, interaction: discord.Interaction):
        result = roll_gacha(self.user_id)
        await interaction.followup.send(result, ephemeral=True)  # Send the actual result after processing
