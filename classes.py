from mongoengine import Document, fields, connect, StringField, IntField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentListField
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
connect('techhub', host=str(os.getenv("MONGODB_URI")))