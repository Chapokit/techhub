from mongoengine import Document, fields, connect, StringField, IntField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentListField
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
connect('techhub', host=str(os.getenv("MONGODB_URI")))

class User(Document):

    # 1. User Information
    discord_id = fields.StringField(required=True)
    user_name = fields.StringField(required=True)

    # 2. Progession Data
    level = fields.IntField(default=1)
    exp = fields.IntField(default=0)