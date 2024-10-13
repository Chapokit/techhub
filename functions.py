from datetime import datetime, timezone
from bson import ObjectId
from mongoengine import Document, fields, connect
import discord
from discord import app_commands
from discord.ext import commands
import random
import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from classes import *

def roll_gacha(user_id):

    user = User.objects(discord_id=user_id).first()

    result = random.randint(1,10000)
    if result == 1:
        pass

def create_user():
    
    user = User(
        discord_id = "999",
        user_name = "Munyin"
    )
    user.save()

