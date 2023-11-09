# MilkshakeEventsBot
Syncs events from an events forum to a Google calendar and bumps them when the event is coming up.

## Running

1. Set up a virtual env for the project with `python -m venv venv`

2. Activate the virtual env with `. venv/bin/activate`

3. Install dependencies `pip install -r requirements.txt`

4. Copy `secrets.example.json` to `secrets.json` and fill with your secrets.

5. Run `python -m events_bot`

## Testing

1. Follow above instructions to setup virtual environment.

2. Install dev dependencies `pip install -r requirements_dev.txt`

3. `pytest`

## Formatting

We format with `black`.
