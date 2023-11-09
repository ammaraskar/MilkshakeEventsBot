from . import bot, events_manager, calendar, tweet_fixer
import json


with open("secrets.json", "r") as f:
    secrets = json.load(f)


event_storage = events_manager.NewlineDelimitedJsonEventStorage("db.json")
calendar = calendar.Calendar(secrets["APP_SCRIPT_URL"], secrets["APP_SCRIPT_TOKEN"])

client = bot.EventsBotClient(event_storage=event_storage, calendar=calendar)
tweet_fixer.register_bot_for_tweet_fixing(client)

client.run(secrets["DISCORD_BOT_TOKEN"])
