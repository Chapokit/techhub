import discord
from discord.ext import commands
from mongoengine.errors import DoesNotExist  # Assuming you use mongoengine for MongoDB
from leader_board import *
from gacha import *

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

# Export the commands
commands_list = [gacha_view, leaderboard_view]
