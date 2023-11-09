# This just losely makes sure the right events get plumbed down. The discordpy
# portion is the yucky IO part of this project so not exactly easy to test.
from events_bot import bot

from unittest.mock import MagicMock, AsyncMock, patch
import pytest


@pytest.mark.asyncio
@patch("events_bot.events_manager.maybe_create_new_event_from_thread")
async def test_launching_bot_and_guilds_available_event_creates_event(
    mock_maybe_create_new_event_from_thread,
):
    """Test that the bot picks up on threads in the event forum when relaunched
    or when it joins a new guild."""
    # This forum has the wrong name so events should not be picked up from it.
    wrong_forum = MagicMock()
    wrong_forum.name = "wrong forum"
    wrong_forum.threads = [MagicMock()]
    wrong_forum.threads[0].id = 1
    # This is the events forum.
    events_forum = MagicMock()
    events_forum.name = bot.EVENTS_FORUM_NAME
    events_forum.threads = [MagicMock()]
    events_forum.threads[0].id = 1
    events_forum.threads[0].fetch_message = AsyncMock(return_value="First message")

    guild = MagicMock()
    guild.forums = [wrong_forum, events_forum]

    await bot.client.on_guild_available(guild)
    mock_maybe_create_new_event_from_thread.assert_called_once_with(
        events_forum.threads[0], "First message"
    )


@pytest.mark.asyncio
@patch("events_bot.events_manager.maybe_create_new_event_from_thread")
async def test_thread_creation_in_wrong_forum_does_not_create_event(
    mock_maybe_create_new_event_from_thread,
):
    thread = MagicMock()
    thread.parent.name = "wrong forum"
    thread.id = 1
    thread.fetch_message = AsyncMock(return_value="First message")

    await bot.client.on_thread_create(thread)
    assert not mock_maybe_create_new_event_from_thread.called


@pytest.mark.asyncio
@patch("events_bot.events_manager.maybe_create_new_event_from_thread")
async def test_thread_creation_in_correct_forum_creates_event(
    mock_maybe_create_new_event_from_thread,
):
    thread = MagicMock()
    thread.parent.name = bot.EVENTS_FORUM_NAME
    thread.id = 1
    thread.fetch_message = AsyncMock(return_value="First message")

    await bot.client.on_thread_create(thread)
    mock_maybe_create_new_event_from_thread.assert_called_once_with(
        thread, "First message"
    )
