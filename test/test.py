import discord
from discord.ext import commands

intents = discord.Intents.default()
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.presences = True 
intents.message_content = True  
intents.guilds = True


bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def create_forum(ctx, forum_name, thread_title, message_content):
    guild = ctx.guild
    try:
        # Create the forum channel using the correct argument 'channel_type'
        forum_channel = await guild.create_text_channel(
            name=forum_name,
            channel_type=discord.ChannelType.forum  # Correct usage
        )
        await ctx.send(f"Forum channel '{forum_name}' created successfully!")

        # Create a new thread in the forum
        thread = await forum_channel.create_thread(name=thread_title)
        await ctx.send(f"Thread '{thread_title}' created in forum '{forum_name}'!")

        # Post a message in the created thread
        await thread.send(message_content)
        await ctx.send(f"Message posted in thread '{thread_title}': {message_content}")

    except discord.Forbidden:
        await ctx.send("I don't have permissions to create a forum channel or thread.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")

@bot.event
async def on_thread_create(thread):
    # check if the thread is in the desired channel
    if thread.parent.name == "test":
        # send a message to the thread
        reply = f"Hello {thread.owner.mention}, please stay in this thread(Don't ping people in <@>) and do not make duplicates. If no one responds to your thread within 1hr, ping `WSC Tech Supporter` Thanks!"
        await thread.send(reply)

bot.run('MTI3NjAyMzk1MjExOTk1NTQ5Nw.GkWPyc.P_2qkzcVWrSu2uQv16a6_-qzG1zv3u07NKeOfg')
