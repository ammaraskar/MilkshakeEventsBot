import datetime


def maybe_create_new_event_from_thread(thread, first_message):
    print(f"  Thread: {thread.name}")
    print(f"    msg: {first_message}")


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
        raise ValueError("Date out of range")

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
