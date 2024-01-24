import traceback
import discord
import requests
from . import events_manager
from . import calendar


EVENTS_FORUM_NAME = "events"


class EventsBotClient(discord.Client):
    def __init__(
        self,
        event_storage: events_manager.EventStorage,
        calendar: calendar.Calendar = None,
    ):
        """Creates an instance of the bot, takes an event_storage to put events
        into based on threads. Optionally takes a calendar to create calendar
        events."""
        self.event_storage = event_storage
        self.calendar = calendar

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
        if event is None:
            # Send a message to the thread to tell the user we were unable to
            # figure out their event's details.
            await thread.send(
                content="I couldn't create an event for your "
                "thread 😢 I probably couldn't understand the date format."
            )
            return
        print(f"Potential new event: {event}")
        if event.calendar_id is not None:
            print("  - Event already on calendar, skipping")
            return
        if self.calendar is None:
            print("  - No calendar instance, skipping")
            return

        try:
            calendar_id = self.calendar.make_calendar_event(
                date=event.date,
                title=event.title,
                description=event.description,
            )
            print(f"  + Event created with id: {calendar_id}")
            event.calendar_id = calendar_id

            self.event_storage.store_events()
            # Send a friendly message to the thread to indicate we picked up
            # their event.
            await thread.send(
                content=f"Event created!"
                "\n\tTitle: {event.title}"
                "\n\tDate: {event.date}"
            )
        except requests.RequestException:
            print("Error adding event to calendar")
            traceback.print_exc()
