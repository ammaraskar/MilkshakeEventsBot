import discord
from . import events_manager


EVENTS_FORUM_NAME = "whoops"


class EventsBotClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_guild_available(self, guild):
        # Handles already existing threads in the forum that the bot may have
        # missed while disconnected.
        print(f"Guild available, {guild.name} {guild.id}")
        for forum in guild.forums:
            if forum.name != EVENTS_FORUM_NAME:
                continue

            print(f"  Forum name: {forum.name}")
            for thread in forum.threads:
                await self.handle_seeing_events_forum_thread(thread)

    async def on_thread_create(self, thread):
        if thread.parent.name != EVENTS_FORUM_NAME:
            return
        await self.handle_seeing_events_forum_thread(thread)

    async def handle_seeing_events_forum_thread(self, thread):
        # Handle seeing a thread in the events forum. Possibly a duplicate
        # of one seen before.
        #
        # Get the first message of the thread. And yup, the first message's id
        # is the same as the thread id. ¯\_(ツ)_/¯
        first_message = await thread.fetch_message(thread.id)
        events_manager.maybe_create_new_event_from_thread(thread, first_message)


intents = discord.Intents.default()
intents.guilds = True

client = EventsBotClient(intents=intents)
