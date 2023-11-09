import datetime
import traceback
from pydantic import BaseModel


class Event(BaseModel):
    # Unique id for the event, used to de-duplicate. Based on the discord
    # message id.
    event_id: str
    title: str
    description: str
    date: datetime.date


def create_event_object_from_thread(
    thread_id, thread_title, thread_creation_date, first_message
):
    (date, title) = try_get_date_title_for_event(thread_creation_date, thread_title)
    return Event(event_id=thread_id, title=title, description=first_message, date=date)


class EventStorage:
    def __init__(self):
        self.events_by_id = {}
        self.events = []

    def try_create_new_event_from_thread(
        self, thread_id, thread_title, thread_creation_date, first_message
    ):
        """Creates a new event based on the thread's details. If successful,
        returns the Event object. If the event already exists or the thread
        is not parseable to an event, returns None."""
        if thread_id in self.events_by_id:
            return None
        print(f"Trying to create new event:")
        print(f"  Thread ID: {thread_id}")
        print(f"      Title: {thread_title}")
        print(f"   Creation: {thread_creation_date}")

        try:
            event_object = create_event_object_from_thread(
                thread_id, thread_title, thread_creation_date, first_message
            )
            self.add_event(event_object)
        except ValueError:
            print(f"ValueError while creating new event")
            traceback.print_exc()
            return None

    def add_event(self, event):
        self.events_by_id[event.event_id] = event
        self.events.append(event)


def maybe_create_new_event_from_thread(thread, first_message):
    print(f"  Thread: {thread.name}")
    print(f"    msg: {first_message}")
    print(f"       : {first_message.content}")


def extract_day_and_month_from_title(title: str):
    """Returns a tuple of (day, month, title) e.g (11, 11, "foo")
    for the event foo on 11th November.

    This is meant to be a lenient parser for people writing titles like:
    * 11/11 Come to my coding party
    * 10/28 X // Y
    * 09/29 Movie night
    * 9/23 Play
    * 1/1      !! Whoops a lot of spaces !!

    Throws a ValueError if there is no extractable day and month.
    """
    # Split on whitespace with max splits of 1 to get the first token.
    possible_date, rest_of_title = title.split(None, 1)

    # Only valid date delimeter for now is slash.
    month, day = possible_date.split("/")
    month, day = int(month), int(day)
    if month < 1 or month > 12 or day < 1 or day > 31:
        raise ValueError(f"Date out of range for: {possible_date}")

    return (day, month, rest_of_title)


def try_get_date_title_for_event(thread_creation_date: datetime.date, title: str):
    """Returns the (date, title) for an event based on its title and when the
    thread mentioning it was created.

    Throws ValueError if the title cannot be parsed."""
    (day, month, title) = extract_day_and_month_from_title(title)

    event_date = datetime.date(thread_creation_date.year, month, day)
    # If the event is for a day/month that's already passed in the current year,
    # it is most likely for the next year!
    if event_date < thread_creation_date:
        event_date = datetime.date(thread_creation_date.year + 1, month, day)

    return event_date, title
