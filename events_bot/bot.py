import discord
from . import events_manager


EVENTS_FORUM_NAME = "whoops"


class EventsBotClient(discord.Client):
    def __init__(self, event_storage: events_manager.EventStorage):
        self.event_storage = event_storage

        intents = discord.Intents.default()
        intents.guilds = True
        # Required to get the contents of the first message in a thread.
        intents.message_content = True
        super().__init__(intents=intents)

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

        # Format the event's description. Start with the message for the thread
        # then add a link to the thread as well as the thread ID for our own
        # tracking purposes.
        description = f"""\
{first_message.content}

{first_message.jump_url}
Discord Thread ID: {thread.id}"""

        event = self.event_storage.try_create_new_event_from_thread(
            thread_id=str(thread.id),
            thread_title=thread.name,
            thread_creation_date=thread.created_at.date(),
            description=description,
        )
        if event is not None:
            print(f"Made new event: {event}")
