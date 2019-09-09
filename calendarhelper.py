from datetime import datetime, date, timedelta, tzinfo, timezone
import caldav
from caldav.elements import dav, cdav
import vobject

def getCaldavEvents(url):
    my_events = []

    date_from = date.today()
    date_to = date.today() + timedelta(7)

    client = caldav.DAVClient(url)
    principal = client.principal()
    calendars = principal.calendars()
    if len(calendars) > 0:
        for calendar in calendars:
            results = calendar.date_search(datetime(date_from.year, date_from.month, date_from.day), datetime(date_to.year, date_to.month, date_to.day))

            for dav_event in results:
                ev = vobject.readOne(dav_event.data)
                new_event = calendarEvent(ev.vevent.dtstart.value, ev.vevent.dtend.value, ev.vevent.summary.valueRepr())
                my_events.append(new_event)

    my_events.sort(key=lambda r: r.datetimestart)
    
    return my_events

class calendarEvent:
    def __init__(self, start, end, summary):
        self.date = date(start.year, start.month, start.day)
        #self.date = datetime.strptime(when, '%Y-%m-%d %H:%M:%S')
        self.datetimestart = datetime(start.year, start.month, start.day, 0,0,0,0, timezone.utc)
        self.datetimeend = datetime(end.year, end.month, end.day, 0,0,0,0, timezone.utc)
        self.allday = True
        if type(start) is datetime:
            #self.datetime = datetime(when.year, when.month, when.day, when.hour, when.minute, 0, 0, timezone.utc)
            self.datetimestart = datetime(start.year, start.month, start.day, start.hour,start.minute,0,0, timezone.utc)
            self.datetimeend = datetime(end.year, end.month, end.day, end.hour,end.minute,0,0, timezone.utc)
            self.allday = False
        self.summary = summary