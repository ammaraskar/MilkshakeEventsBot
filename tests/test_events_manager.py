from events_bot import events_manager
import datetime
import pytest

default_thread_creation_date = datetime.date(2022, 1, 1)


def get_current_year():
    return datetime.date.today().year


def test_title_parsing_works():
    (date, title) = events_manager.extract_date_from_title(
        "11/11 Come to my coding party", default_thread_creation_date
    )
    assert date == datetime.date(2022, 11, 11)
    assert title == "Come to my coding party"

    (date, title) = events_manager.extract_date_from_title(
        "10/28 X // Y", default_thread_creation_date
    )
    assert date == datetime.date(2022, 10, 28)
    assert title == "X // Y"

    (date, title) = events_manager.extract_date_from_title(
        "9/23 Play", default_thread_creation_date
    )
    assert date == datetime.date(2022, 9, 23)
    assert title == "Play"

    (date, title) = events_manager.extract_date_from_title(
        "1/1      !! Whoops a lot of spaces !!", default_thread_creation_date
    )
    assert date == datetime.date(2022, 1, 1)
    assert title == "!! Whoops a lot of spaces !!"

    (date, title) = events_manager.extract_date_from_title(
        "2028/07/04 Event with specified year",
        # If a year is specified, the default won't kick in.
        default_thread_creation_date,
    )
    assert date == datetime.date(2028, 7, 4)
    assert title == "Event with specified year"


def test_title_parsing_fails_on_wrong_formats():
    with pytest.raises(ValueError):
        events_manager.extract_date_from_title("boo", default_thread_creation_date)

    with pytest.raises(ValueError):
        events_manager.extract_date_from_title(
            "0/0 Pranked", default_thread_creation_date
        )


def test_event_date_parsing_works():
    thread_time = datetime.date(2022, 8, 1)
    (date, title) = events_manager.try_get_date_title_for_event(
        thread_time, "9/21 Concert number one"
    )

    assert date.year == 2022
    assert date.month == 9
    assert date.day == 21
    assert title == "Concert number one"


def test_event_date_parsing_works_for_events_next_year():
    # Thread created in August for an event in January.
    thread_time = datetime.date(2022, 8, 1)
    (date, title) = events_manager.try_get_date_title_for_event(
        thread_time, "1/21 Concert"
    )
    assert date.year == 2023
    assert date.month == 1
    assert date.day == 21
    assert title == "Concert"

    # A Thread that specifies a year that already happened. This is more likely
    # to happen around the new year.
    thread_time = datetime.date(2022, 1, 22)
    (date, title) = events_manager.try_get_date_title_for_event(
        thread_time, "2021-04-10 The Beths"
    )
    assert date.year == 2022
    assert date.month == 4
    assert date.day == 10
    assert title == "The Beths"


def test_event_storage_creates_new_event():
    storage = events_manager.EventStorage()
    created_event = storage.try_create_new_event_from_thread(
        thread_id="1",
        thread_title="1/1/23 Post New Years",
        thread_creation_date=datetime.date(2022, 12, 20),
        description="Come to\nhell!!!",
    )
    assert "1" in storage.events_by_id
    assert len(storage.events) == 1
    assert storage.events[0] == created_event
    assert storage.events[0].event_id == "1"
    assert storage.events[0].title == "Post New Years"
    assert storage.events[0].description == "Come to\nhell!!!"
    assert storage.events[0].date == datetime.date(2023, 1, 1)


def test_event_storage_returns_none_on_duplicate_event():
    storage = events_manager.EventStorage()
    created_event = storage.try_create_new_event_from_thread(
        thread_id="1",
        thread_title="1/1 Post New Years",
        thread_creation_date=datetime.date(2022, 12, 20),
        description="Come to\nhell!!!",
    )
    assert created_event is not None

    event_again = storage.try_create_new_event_from_thread(
        thread_id="1",
        thread_title="1/1 No No No",
        thread_creation_date=datetime.date(2022, 12, 20),
        description="My bad",
    )
    # Should just return the initial event. In the future this may update the
    # existing event.
    assert event_again == created_event


def test_event_storage_returns_none_on_unparsable_event():
    storage = events_manager.EventStorage()
    event = storage.try_create_new_event_from_thread(
        thread_id="1",
        thread_title="meta",
        thread_creation_date=datetime.date(2022, 12, 20),
        description="Not an event",
    )
    assert event is None


def test_flat_file_storage_loads_existing_events(tmp_path):
    existing_events = """\
{"event_id": "1", "title": "Hi", "description": "come to my event", "date": "2022-01-01"}
{"event_id": "2", "title": "Bye", "description": "that was fun", "date": "2022-02-01"}
"""

    db_path = tmp_path / "db.json"
    db_path.write_text(existing_events)

    storage = events_manager.NewlineDelimitedJsonEventStorage(db_path)
    assert len(storage.events) == 2
    assert storage.events[0].title == "Hi"
    assert storage.events[1].title == "Bye"


def test_flat_file_storage_writes_event_to_file(tmp_path):
    db_path = tmp_path / "db.json"
    storage = events_manager.NewlineDelimitedJsonEventStorage(db_path)

    event = storage.try_create_new_event_from_thread(
        thread_id="1",
        thread_title="1/1 Post New Years",
        thread_creation_date=datetime.date(2022, 12, 20),
        description="Come to\nhell!!!",
    )
    output_file = db_path.read_text()
    assert (
        output_file
        == '{"event_id":"1","title":"Post New Years","description":"Come to\\nhell!!!","date":"2023-01-01","calendar_id":null}\n'
    )


def test_flat_file_storage_updates_existing_event(tmp_path):
    db_path = tmp_path / "db.json"
    storage = events_manager.NewlineDelimitedJsonEventStorage(db_path)

    event = storage.try_create_new_event_from_thread(
        thread_id="1",
        thread_title="1/1 I will update",
        thread_creation_date=datetime.date(2022, 12, 20),
        description="Description",
    )

    event.calendar_id = "CAL-123"
    storage.store_events()

    output_file = db_path.read_text()
    assert (
        output_file
        == '{"event_id":"1","title":"I will update","description":"Description","date":"2023-01-01","calendar_id":"CAL-123"}\n'
    )
