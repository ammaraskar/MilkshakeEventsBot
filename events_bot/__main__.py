from . import bot, events_manager
import json


with open("secrets.json", "r") as f:
    secrets = json.load(f)


event_storage = events_manager.NewlineDelimitedJsonEventStorage("db.json")
client = bot.EventsBotClient(event_storage=event_storage)
client.run(secrets["DISCORD_BOT_TOKEN"])
