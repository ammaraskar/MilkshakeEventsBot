const ACCESS_TOKEN = "...";
const CALENDAR_NAME = "Milkshake Events";


function doPost(e) {
    let result;
    const params = JSON.parse(e.postData.contents);
    const token = params.token;

    if(token === ACCESS_TOKEN) {
        result = createCalendarEventFromRequest(params);
    } else {
        result = {
            'error': 'Forbidden',
            'message': 'You do not have access to this resource.'
        }
    }
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
}

function createCalendarEventFromRequest(params) {
  return createCalendarEvent(params.title, new Date(params.date), params.description);
}

function createCalendarEvent(title, date, description) {
  const calendars = CalendarApp.getCalendarsByName(CALENDAR_NAME);
  if (calendars.length == 0) {
    return {"error": "Calendar called " + CALENDAR_NAME + " not found"};
  }
  if (calendars.length > 1) {
    return {"error": "Too many calendars called " + CALENDAR_NAME};
  }
  const calendar = calendars[0];
  const event = calendar.createAllDayEvent(title, date, {description: description});
  return {"event_id": event.getId()};
}
