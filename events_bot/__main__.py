from .bot import client
import json


with open("secrets.json", "r") as f:
    secrets = json.load(f)

client.run(secrets["DISCORD_BOT_TOKEN"])
