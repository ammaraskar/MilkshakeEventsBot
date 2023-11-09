from . import bot, events_manager
import json


with open("secrets.json", "r") as f:
    secrets = json.load(f)


client = bot.EventsBotClient(events_manager.EventStorage())
client.run(secrets["DISCORD_BOT_TOKEN"])
