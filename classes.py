from mongoengine import Document, fields, connect
from dotenv import load_dotenv
import os

load_dotenv()
connect('techhub', host=str(os.getenv("MONGODB_URI")))

class User(Document):

    # 1. User Informa   tion
    discord_id = fields.StringField(required=True)
    user_name = fields.StringField(required=True)
    role = fields.StringField(default="None")

    # 2. Progession Data
    level = fields.IntField(default=1)
    exp = fields.IntField(default=0)

    # 3. Inventory (Dictionary field)
    inventory = fields.DictField(default=lambda: {'HCoin': 0, 'Big Enter': 0, 'JBL': 0, 'Rimuru': 0,
                                                  'Divoom': 0, 'Mechanical': 0})
    # 4. Traded Items (List of strings)
    traded_items = fields.ListField(fields.StringField(), default=list)

    # 5. Gacha Roll
    roll_count = fields.IntField(default=0)
    roll_all_time = fields.IntField(default=0)
