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
