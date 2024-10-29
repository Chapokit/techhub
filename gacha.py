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



class ResendGacha(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Roll Again 🎰", style=discord.ButtonStyle.primary)
    async def roll_again(self, interaction: discord.Interaction, button: discord.ui.Button):

        gacha_view = GachaView()
        await interaction.response.send_message("Let's roll again!", view=gacha_view, ephemeral=True)

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__()

    async def countdown(self, interaction: discord.Interaction):
        # Send the countdown message in parts
        await interaction.followup.send("Rolling in 3...", ephemeral=True)
        await asyncio.sleep(1)
        await interaction.followup.send("Rolling in 2...", ephemeral=True)
        await asyncio.sleep(1)
        await interaction.followup.send("Rolling in 1...", ephemeral=True)
        await asyncio.sleep(1)

    async def send_gacha_results(self, interaction: discord.Interaction, results, user, HCoins):

        embed = discord.Embed(title="Gacha Results", description="You got:")
        image_url = None

        if len(results) > 1:
            for result in results:              
                string = result.split(":")[1].split("x")[0].strip()

                if string == 'HCoin':
                    embed.add_field(name = f"{result}", value="", inline=False)                   
                else:
                    embed.add_field(name = f"{result}", value="", inline=False)

        else:
            string = results[0]
            result = string.split(":")[1].split("x")[0].strip()

            if result == 'HCoin':
                embed.add_field(name = f"{string}", value="", inline=False)
            else:
                embed.add_field(name = f"{result}", value="", inline=False)
 
            if result == "HCoin":
                image_url = "picture/hcoin.png"
            elif result == "Big Enter":
                image_url = "picture/bigenter.jpg"
            elif result == "JBL":
                image_url = "picture/jbl.jpg"
            elif result == "Rimuru":
                image_url = "picture/rimuru.png"
            elif result == "Divoom":
                image_url = "picture/divoom.png"
            elif result == "Mechanical":
                image_url = "picture/mechanical.jpg"
            else:
                image_url = None  # No image if no match found

        if image_url is not None:
            with open(image_url, 'rb') as file:
                image_file = discord.File(file, os.path.basename(image_url))
            embed.set_image(url=f"attachment://{os.path.basename(image_url)}")
        else:
            image_file = None  # No image to send
            # You can handle this case as needed, e.g., send without an image

        # Send the embed message with the results
        if image_file is not None:
            await interaction.followup.send(embed=embed, file=image_file, ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, ephemeral=True)  # Send without image



        # Send the ResendGacha view to allow the user to roll again
        resend_gacha = ResendGacha()
        await interaction.followup.send("Do you want to roll again?", view=resend_gacha, ephemeral=True)

    @discord.ui.button(label="Roll Gacha x1 🎰", style=discord.ButtonStyle.primary, row=0)
    async def one_roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        user = User.objects(discord_id=str(interaction.user.id)).first()
        if user.roll_count > 0:
            user.roll_count -= 1
            user.roll_all_time += 1
            user.save()

            await interaction.response.defer(ephemeral=True)
            await self.countdown(interaction)

            common_item = ['HCoin']
            rare_item = ['Big Enter', 'JBL', 'Rimuru']
            legend_item = ['Divoom', 'Mechanical']

            roll, HCoins = roll_gacha(interaction.user.id)
            if roll in common_item:
                result = f"🟩 Common: {roll} x{HCoins}"
            elif roll in rare_item:
                result = f"🟦 Rare: {roll}"
            elif roll in legend_item:
                result = f"🟨 Legendary: {roll}"
            else:
                result = f"🟩 Common: {roll}"

            await self.send_gacha_results(interaction, [result], user, HCoins)
        
        else:
            await interaction.response.send_message(f"You don't have enough gacha points. {user.roll_count} rolls left.", ephemeral=True)
        

    @discord.ui.button(label="Roll Gacha x10 🎰", style=discord.ButtonStyle.primary, row=0)
    async def ten_rolls(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = User.objects(discord_id=str(interaction.user.id)).first()

        if user.roll_count >= 10:
            user.roll_count -= 10
            user.roll_all_time += 10
            user.save()

            await interaction.response.defer(ephemeral=True)
            await self.countdown(interaction)

            common_item = ['HCoin']
            rare_item = ['Big Enter', 'JBL', 'Rimuru']
            legend_item = ['Divoom', 'Mechanical']

            results = []
            for _ in range(10):
                result, HCoins = roll_gacha(interaction.user.id)

                if result in common_item:
                    results.append(f"🟩 Common: {result} x{HCoins}")
                elif result in rare_item:
                    results.append(f"🟦  Rare: {result}")
                elif result in legend_item:
                    results.append(f"🟨 Legendary: {result}")

            await self.send_gacha_results(interaction, results, user, HCoins)
        
        else:
            await interaction.response.send_message(f"You don't have enough gacha points. {user.roll_count} rolls left.", ephemeral=True)

    @discord.ui.button(label="Check Gacha Rate %", style=discord.ButtonStyle.primary, row=0)
    async def show_rate(self, interaction: discord.Interaction, button: discord.ui.Button):

        gacha_rate = check_rate(user_id=interaction.user.id)
        user = User.objects(discord_id=str(interaction.user.id)).first()

        embed = discord.Embed(
                            title="**GACHA RATE 🎰**",
                            description=(
                                f"**User Name:** ``{interaction.user.name}``\n"
                                f"**Level:** ``{user.level}``\n"
                                f"**Gacha Rate:**\n"
                                f"🟩 **Common%:** ``{gacha_rate['Common%']:.2f}%``\n"
                                f"🟦 **Rare%:** ``{gacha_rate['Rare%']:.2f}%``\n"
                                f"🟨 **Legend%:** ``{gacha_rate['Legend%']:.2f}%``\n\n"
                                "Your gacha rates depend on your level."
                            ),
                            color=discord.Color.darker_gray()
                        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class GachaResult(discord.ui.View):
    def __init__(self, user_id, discord_user):
        super().__init__()

        self.user_id = user_id
        self.discord_user = discord_user

    async def display_result(self, interaction: discord.Interaction):

        result = roll_gacha(self.user_id)
        await interaction.followup.send(result, ephemeral=True)

        # Send the ResendGacha view to allow the user to roll again
        resend_gacha = ResendGacha()
        await interaction.followup.send("Do you want to roll again?", view=resend_gacha, ephemeral=True)

