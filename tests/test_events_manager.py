from events_bot import events_manager
import datetime
import pytest


def test_title_parsing_works():
    (day, month, title) = events_manager.extract_day_and_month_from_title(
        "11/11 Come to my coding party"
    )
    assert day == 11
    assert month == 11
    assert title == "Come to my coding party"

    (day, month, title) = events_manager.extract_day_and_month_from_title(
        "10/28 X // Y"
    )
    assert day == 28
    assert month == 10
    assert title == "X // Y"

    (day, month, title) = events_manager.extract_day_and_month_from_title("9/23 Play")
    assert day == 23
    assert month == 9
    assert title == "Play"

    (day, month, title) = events_manager.extract_day_and_month_from_title(
        "1/1      !! Whoops a lot of spaces !!"
    )
    assert day == 1
    assert month == 1
    assert title == "!! Whoops a lot of spaces !!"


def test_title_parsing_fails_on_wrong_formats():
    with pytest.raises(ValueError):
        events_manager.extract_day_and_month_from_title("boo")

    with pytest.raises(ValueError):
        events_manager.extract_day_and_month_from_title("0/0 Pranked")

    with pytest.raises(ValueError):
        events_manager.extract_day_and_month_from_title("1-2 Pranked")


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


def test_event_storage_creates_new_event():
    storage = events_manager.EventStorage()
    created_event = storage.try_create_new_event_from_thread(
        thread_id="1",
        thread_title="1/1 Post New Years",
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
