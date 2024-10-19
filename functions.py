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
    user = User.objects(discord_id=str(user_id)).first()

    effective_level = user.level
    max_level = 100
    effective_level = min(effective_level, max_level)

    # Calculate rarities based on level
    common_rate = 100 - (0.75 * effective_level ** 1.5 + 1)
    legend_rate = (100 - common_rate) * 0.03 * effective_level
    rare_rate = 100 - common_rate - legend_rate

    # Generate a random number to determine the outcome
    result = random.uniform(0, 100)

    if result <= common_rate:
        # Common roll logic
        fragment_number = random.randint(1, 3)
        user.fragment[f"fragment{fragment_number}"] += 1
        user.save()
        return f"Common Fragment {fragment_number}"

    elif result <= common_rate + rare_rate:
        # Rare roll logic
        fragment_number = random.randint(1, 3)
        user.fragment[f"fragment{fragment_number}"] += 1
        user.save()
        return f"Rare Fragment {fragment_number}"

    else:
        # Legend roll logic
        fragment_number = random.randint(1, 3)
        user.fragment[f"fragment{fragment_number}"] += 1
        user.save()
        return f"Legendary Fragment {fragment_number}"

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



