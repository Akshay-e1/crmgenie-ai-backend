from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URI"),
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

print(client.admin.command("ping"))