from datetime import datetime, timezone
from bson import ObjectId
from mongoengine import Document, fields, connect
from mongoengine import DoesNotExist
import discord
from discord import app_commands
from discord.ext import commands
import random
import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


from classes import *

import random

def roll_gacha(user_id):
    common_item = ['HCoin']
    rare_item = ['Big Enter', 'JBL', 'Rimuru']
    legend_item = ['Dvoom', 'Mechanical']

    user = User.objects(discord_id=str(user_id)).first()

    if not user:
        raise ValueError("User not found")

    effective_level = user.level
    max_level = 100
    effective_level = min(effective_level, max_level)

    # Calculate rarities based on level
    common_rate = 100 - (0.75 * effective_level ** 1.5 + 1)
    legend_rate = (100 - common_rate) * 0.03
    rare_rate = 100 - common_rate - legend_rate

    # Generate a random number to determine the outcome
    result = random.uniform(0, 100)

    if result <= common_rate:
        # Common roll logic
        gacha_result = random.choice(common_item)
    elif result <= common_rate + rare_rate:
        # Rare roll logic
        gacha_result = random.choice(rare_item)
    else:
        # Legend roll logic
        gacha_result = random.choice(legend_item)

    # Increment inventory count for the rolled item
    user.inventory[gacha_result] += 1
    user.save()

    return gacha_result
def check_rate(user_id):
    user = User.objects(discord_id=str(user_id)).first()

    effective_level = user.level
    max_level = 100
    effective_level = min(effective_level, max_level)

    # Calculate rarities based on level
    common_rate = 100 - (0.75 * effective_level ** 1.5 + 1)
    legend_rate = (100 - common_rate) * 0.03 * effective_level
    rare_rate = 100 - common_rate - legend_rate

    return {
        "Common%": common_rate,
        "Rare%": rare_rate,
        "Legend%": legend_rate
    }
    
def exp_needed_for_level(level):
    base_exp = 100
    multiplier = 1.1
    exp_needed = base_exp * (multiplier ** level)
    return exp_needed

def level_up(user_id):
    user = User.objects(discord_id=user_id).first()

    exp_needed = exp_needed_for_level(user.level)
    if user.exp >= exp_needed:
        user.exp -= exp_needed
        user.level += 1
    user.save()

def create_user():
    
    user = User(
        discord_id = "888",
        user_name = "Munyin"
    )
    user.save()



