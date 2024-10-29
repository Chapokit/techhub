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


class Forum:
    def __init__(self, guild: discord.Guild, forum_name: str, thread_title: str, message_content: str, topic: str = None):
        self.guild = guild
        self.forum_name = forum_name
        self.thread_title = thread_title
        self.message_content = message_content
        self.topic = topic or f"Discussion about {forum_name}"
        self.forum_channel = None

    async def create_forum_channel(self, slowmode_delay: int = 0, nsfw: bool = False, reason: str = None):
        """Create the forum channel."""
        try:
            self.forum_channel = await self.guild.create_forum_channel(
                name=self.forum_name,
                topic=self.topic,
                slowmode_delay=slowmode_delay,
                nsfw=nsfw,
                reason=reason or "Creating a new forum channel"
            )
            return f"Forum channel '{self.forum_name}' created successfully!"
        except discord.Forbidden:
            return "I don't have permissions to create a forum channel."
        except discord.HTTPException as e:
            return f"An error occurred: {e}"

    async def create_thread(self):
        """Create a thread in the forum channel."""
        if not self.forum_channel:
            return "Forum channel has not been created yet."
        
        try:
            thread = await self.forum_channel.create_thread(name=self.thread_title)
            await thread.send(self.message_content)
            return f"Thread '{self.thread_title}' created in forum '{self.forum_name}' and message posted."
        except discord.Forbidden:
            return "I don't have permissions to create a thread."
        except discord.HTTPException as e:
            return f"An error occurred: {e}"

# # Command to trigger forum creation
# @commands.command(name="create_forum")
# async def create_forum(ctx, forum_name, thread_title, message_content):
#     guild = ctx.guild
    
#     # Initialize the Forum class
#     forum = Forum(guild, forum_name, thread_title, message_content)
    
#     # Create the forum channel
#     create_forum_msg = await forum.create_forum_channel()
#     await ctx.send(create_forum_msg)

#     # Create a thread in the forum
#     create_thread_msg = await forum.create_thread()
#     await ctx.send(create_thread_msg)

@bot.command(name="create_post_in_forum")
async def create_post_in_forum(ctx, forum_channel_id: int, thread_name: str, *, content: str):
    # Fetch the forum channel using the provided channel ID
    forum_channel = bot.get_channel(forum_channel_id)  # This will return None if not found
    
    if forum_channel is None:
        try:
            forum_channel = await bot.fetch_channel(forum_channel_id)
        except discord.NotFound:
            await ctx.send("Channel not found. Please check the channel ID.")
            return
        except discord.Forbidden:
            await ctx.send("I do not have permission to access this channel.")
            return
        except Exception as e:
            await ctx.send(f"Failed to fetch forum channel: {str(e)}")
            return

    # Check if the channel is indeed a forum channel
    if isinstance(forum_channel, discord.ForumChannel):
        try:
            # Create a new thread (post) in the forum channel
            thread = await forum_channel.create_thread(
                name=thread_name,
                content=content,
                auto_archive_duration=60,  # Auto-archive after 60 minutes
                reason="Creating a new post through command"
            )
            await ctx.send(f"Post created successfully in {forum_channel.name}! Thread: {thread.mention}")
        except Exception as e:
            await ctx.send(f"Failed to create post: {str(e)}")
    else:
        await ctx.send("The specified channel is not a forum channel.")

@bot.command(name="create")
async def create(ctx, arg: str):
    channel = await ctx.guild.create_text_channel(arg, category=discord.utils.get(ctx.guild.categories, name='FORUM'))


# Export the commands
commands_list = [gacha_view, leaderboard_view, create_post_in_forum, create]
