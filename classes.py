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
    inventory = fields.DictField(default=lambda: {"fragment1": 0, "fragment2": 0, "fragment3": 0
                                                  , 'HCoin': 0, 'Big Enter': 0, 'JBL': 0, 'Rimuru': 0,
                                                  'Dvoom': 0, 'Mechanical': 0})

    # 4. Gacha Roll
    roll_count = fields.IntField(default=0)
    roll_all_time = fields.IntField(default=0)
