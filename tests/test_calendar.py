from events_bot.calendar import Calendar
import datetime
import responses
import pytest


TEST_CALENDAR_URL = "https://calendar-endpoint.com/foo/bar/exec"
TEST_CALENDAR_TOKEN = "test-token"


@responses.activate
def test_posts_fails_when_error_in_response():
    responses.add(
        responses.POST,
        TEST_CALENDAR_URL,
        json={"error": "forbidden"},
        status=200,
    )
    calendar = Calendar(TEST_CALENDAR_URL, "wrong-token")
    with pytest.raises(RuntimeError) as exc_info:
        calendar.make_calendar_event(
            date=datetime.date(2022, 11, 11),
            title="Test title",
            description="test description",
        )

    assert "Error from calendar endpoint" in str(exc_info.value)
    assert "forbidden" in str(exc_info.value)


@responses.activate
def test_post_returns_calendar_id_when_succeeds():
    responses.add(
        responses.POST,
        TEST_CALENDAR_URL,
        json={"event_id": "GCAL-1234"},
        status=200,
    )
    calendar = Calendar(TEST_CALENDAR_URL, TEST_CALENDAR_TOKEN)
    event_id = calendar.make_calendar_event(
        date=datetime.date(2022, 11, 11),
        title="Test title",
        description="test description",
    )
    assert event_id == "GCAL-1234"
