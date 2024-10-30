import discord
from discord.ext import commands
from mongoengine.errors import DoesNotExist  # Assuming you use mongoengine for MongoDB
from leader_board import *
from gacha import *

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.presences = True 
intents.message_content = True  
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


ALLOWED_CHANNEL_ID = 1300038617166643211

def is_in_allowed_channel(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL_ID

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


# Export the commands
commands_list = [gacha_view, leaderboard_view, create_channel]
