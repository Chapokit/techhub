import discord
from discord.ext import commands
from mongoengine.errors import DoesNotExist  # Assuming you use mongoengine for MongoDB
from leader_board import *
from gacha import *
import asyncio
from discord import ButtonStyle, Interaction
from discord.ui import Button, View

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.presences = True 
intents.message_content = True  
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# BOT COMMAND CHANNEL
ALLOWED_CHANNEL_ID = 1289131500469747823
ADMIN_CHANNEL_ID = 1301130554405818389

def is_in_allowed_channel(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL_ID

def is_in_allowed_admin_channel(ctx):
    return ctx.channel.id == ADMIN_CHANNEL_ID

@commands.command(name="gacha", help="Perform a gacha pull")
async def gacha_view(ctx):
    if not is_in_allowed_channel(ctx):
        allowed_channel_mention = f"<#{ALLOWED_CHANNEL_ID}>"
        embed = discord.Embed(title="Error", description=f"Please use the command in {allowed_channel_mention}.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if User.objects(discord_id=str(ctx.author.id)).first():
        view = GachaView()
        await ctx.send("Select an option below.", view=view)
    else:
        admin_mention = f"<@{458231861588656128}>"
        embed = discord.Embed(title="Error", description=f"Please contact the admin {admin_mention}.", color=discord.Color.red())
        await ctx.send(embed=embed)

@commands.command(name="leaderboard", help="Display Leaderboard")
async def leaderboard_view(ctx):
    if not is_in_allowed_channel(ctx):
        allowed_channel_mention = f"<#{ALLOWED_CHANNEL_ID}>"
        embed = discord.Embed(title="Error", description=f"Please use the command in {allowed_channel_mention}.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    leaderboard = Leaderboard(bot=ctx.bot, channel_id=ctx.channel.id)
    await leaderboard.display_leaderboard()

@commands.command(name="create_channel")
@commands.has_permissions(manage_channels=True)  # Ensure the user has permission to manage channels
async def create_channel(ctx, channel_name: str, category_name: str):
    guild = ctx.guild  # Get the server (guild) where the command was used

    # Find the category by name
    category = discord.utils.get(guild.categories, name=category_name)

    if category is None:
        await ctx.send(f"Category '{category_name}' not found.")
        return

    try:
        # Create a text channel in the specified category
        new_text_channel = await guild.create_text_channel(channel_name, category=category)

        # Create a forum channel in the specified category
        new_forum_channel = await guild.create_forum(f"{channel_name}-forum", category=category)

        # Create a thread inside the forum
        thread = await new_forum_channel.create_thread(
            name=f"{channel_name}-discussion",
            content="Initial thread post content here",  # Initial post content
            auto_archive_duration=1440  # Auto-archive after 24 hours of inactivity
        )

        await ctx.send(f"Text channel '{channel_name}', forum '{new_forum_channel.name}', and thread '{thread.name}' created successfully!")
    except Exception as e:
        await ctx.send(f"Failed to create channels: {e}")

@commands.command(name="send_message_all")
@commands.has_permissions(administrator=True)  # Only admins can use this command
async def send_message_all(ctx, *, message: str):
    
    if not is_in_allowed_admin_channel(ctx):
        allowed_channel_mention = f"<#{1301130554405818389}>"
        embed = discord.Embed(title="Error", description=f"Please use the command in {allowed_channel_mention}.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    guild = ctx.guild  # Get the server (guild)
    
    if not message:
        await ctx.send("You need to provide a message to send.")
        return

    # Confirming the message before sending to all members
    await ctx.send(f"Sending this message to all members:\n\n{message}\n\nType 'yes' to confirm.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "yes"

    try:
        # Use ctx.bot.wait_for to ensure we're working with the correct bot instance
        await ctx.bot.wait_for("message", timeout=30.0, check=check)  # Wait for confirmation
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Canceling message.")
        return

    # Send message to all members
    sent_count = 0
    failed_count = 0

    for member in guild.members:
        if member.bot:  # Skip bots
            continue
        try:
            await member.send(message)  # Send the private message (DM)
            sent_count += 1
        except discord.Forbidden:
            failed_count += 1  # Failed to send (likely due to privacy settings)

        # Add a short delay to avoid rate limits
        await asyncio.sleep(1)

    # Provide feedback to the user
    await ctx.send(f"Message sent to {sent_count} members. Failed to send to {failed_count} members (likely due to privacy settings).")



# Export the commands
commands_list = [gacha_view, leaderboard_view, send_message_all]

