import requests
import datetime


class Calendar:
    """Adds calendar events using a POST request to an apps script URL."""

    def __init__(self, app_script_url, app_script_token):
        self.app_script_url = app_script_url
        self.app_script_token = app_script_token

    def make_calendar_event(self, date: datetime.date, title: str, description: str):
        """Makes a calendar event returning its created id if successful."""
        body = {
            "token": self.app_script_token,
            "date": date.isoformat(),
            "title": title,
            "description": description,
        }
        import json
        r = requests.post(self.app_script_url, json=body)

        if "Exception:" in r.text:
            raise RuntimeError(f"Exception in apps script: {r.text}")

        response = r.json()
        if "error" in response:
            raise RuntimeError(f"Error from calendar endpoint: {response}")
        return response["event_id"]
