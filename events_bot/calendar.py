import requests
import datetime


class Calendar:
    """Adds calendar events using a POST request to an apps script URL."""

    def __init__(self, app_script_url, app_script_token):
        self.app_script_url = app_script_url
        self.app_script_token = app_script_token

    def make_calendar_event(self, date, title, description):
        """Makes a calendar event returning its created id if successful."""
        body = {
            "token": self.app_script_token,
        }
