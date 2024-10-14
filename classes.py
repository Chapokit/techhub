from mongoengine import Document, fields, connect
from dotenv import load_dotenv
import os

load_dotenv()
connect('techhub', host=str(os.getenv("MONGODB_URI")))

class User(Document):

    # 1. User Information
    discord_id = fields.StringField(required=True)
    user_name = fields.StringField(required=True)

    # 2. Progession Data
    level = fields.IntField(default=1)
    exp = fields.IntField(default=0)

    # 3. Inventory (Dictionary field)
    fragment = fields.DictField(default=lambda: {"a": [0], "b": [0], "c": [0]})

    # 4. Gacha Roll
    roll_count = fields.IntField(default=0)
