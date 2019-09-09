from PIL import Image, ImageDraw, ImageFont
from urllib.request import Request, urlopen
from urllib.parse import quote, unquote
import json
import pytz
import os
from calendarhelper import getCaldavEvents, calendarEvent
from datetime import datetime, date, timedelta, tzinfo, timezone
from tzlocal import get_localzone
from dotenv import load_dotenv
load_dotenv()

import locale
locale.setlocale(locale.LC_ALL, os.getenv('LOCALE'))

home_assistant_base_url = os.getenv('HOME_ASSISTANT_BASE_URL')
home_assistant_access_token = os.getenv('HOME_ASSISTANT_ACCESS_TOKEN')
caldav_url = os.getenv('CALDAV_URL')

display_height = int(os.getenv('DISPLAY_WIDTH'))
display_width = int(os.getenv('DISPLAY_HEIGHT'))

localtimezone = get_localzone()

# cheat sheet https://cdn.materialdesignicons.com/4.3.95/
weather_icons = {
  'cloudy': '%EF%96%90',
  'fog': '%EF%96%91',
  'hail': '%EF%96%92',
  'hurricane': '%EF%A2%97',
  'lightning': '%EF%96%93',
  'lightning-rainy': '%EF%99%BD',
  'night': '%EF%96%94',
  'partlycloudy': '%EF%96%95',
  'pouring': '%EF%96%96',
  'rainy': '%EF%96%97',
  'snowy': '%EF%96%98',
  'snowy-rainy': '%EF%99%BE',
  'sunny': "%EF%96%99",
  'sunset': '%EF%96%9A',
  'sunset-down': '%EF%96%9B',
  'sunset-up': '%EF%96%9C',
  'windy': '%EF%96%9D',
  'thermometer': '\uF50F',
  'humidity': '\uF58E',
  'sunset': '\uF59B',
  'sunrise': '\uF59C'
}

def get_ha_sensor_state(state):
  try:
    req = Request(home_assistant_base_url + state)
    req.add_header('Authorization', 'Bearer ' + home_assistant_access_token)
    content = urlopen(req).read()
    sensor_data = json.loads(content.decode("utf-8"))
    return sensor_data
  except Exception as e:
    print("Error reading " + state + ": " + str(e))
    return None

def create_image():

  # init black/white image
  black_image = Image.new('1', (display_width, display_height), 255)
  draw_black = ImageDraw.Draw(black_image)

  # init fonts
  fontForecastToday = ImageFont.truetype('materialdesignicons-webfont.ttf', 48)
  fontForecast = ImageFont.truetype('materialdesignicons-webfont.ttf', 32)
  fontThermometer = ImageFont.truetype('SourceSansPro-Bold.ttf', 36)
  fontSun = ImageFont.truetype('SourceSansPro-Bold.ttf', 24)
  fontEventToday = ImageFont.truetype('SourceSansPro-Regular.ttf', 26)
  fontEvent = ImageFont.truetype('SourceSansPro-Regular.ttf', 24)
  fontDateToday = ImageFont.truetype('SourceSansPro-Bold.ttf', 40)
  fontDate = ImageFont.truetype('SourceSansPro-Bold.ttf', 26)

  now = datetime.now().astimezone(localtimezone)

  # get weather forecast
  weather_data = get_ha_sensor_state('states/weather.smhi_home') # or states/weather.dark_sky

  # get sunrise/sunset
  sun_data = get_ha_sensor_state('states/sun.sun')['attributes']

  # get sensor data
  outdoor_sensor = get_ha_sensor_state('states/sensor.outdoor_2')

  # get calendar events
  events = getCaldavEvents(caldav_url)


  # draw today
  msg = now.strftime('%A %-d/%-m')
  text_w, text_h = draw_black.textsize(msg, font = fontDateToday)
  draw_black.text((10, 10), msg, font = fontDateToday, fill = 0)

  # draw today's forecast
  if weather_data is not None:
    draw_black.text((245, 10), unquote(weather_icons[weather_data['attributes']['forecast'][0]['condition']]), font = fontForecastToday, fill = 0)
    draw_black.text((295, 10), str(weather_data['attributes']['forecast'][0]['temperature']) + ' °C' , font = fontThermometer, fill = 0)

  # draw current outdoor temp
  if outdoor_sensor is not None:
    str_current_outdoor_temp = str(outdoor_sensor["state"] + ' ' + outdoor_sensor['attributes']['unit_of_measurement'])
    text_w, text_h = draw_black.textsize(str_current_outdoor_temp, font = fontThermometer)
    current_outdoor_temp_y = display_height - 10 - text_h
    draw_black.text((35, current_outdoor_temp_y), str_current_outdoor_temp, font = fontThermometer, fill = 0)
    draw_black.text((0, current_outdoor_temp_y+10), unquote(weather_icons[outdoor_sensor['attributes']['icon'][4:]]), font = fontForecast, fill = 0)

  # draw sunrise/sunset hours
  if sun_data is not None:
    sunrise = pytz.utc.localize(datetime.strptime(sun_data['next_rising'][:-6], '%Y-%m-%dT%H:%M:%S'))
    sunset = pytz.utc.localize(datetime.strptime(sun_data['next_setting'][:-6], '%Y-%m-%dT%H:%M:%S'))

    draw_black.text((200, current_outdoor_temp_y+10), sunrise.astimezone(localtimezone).strftime("%H:%M",), font = fontSun, fill = 0)
    draw_black.text((170, current_outdoor_temp_y+10), unquote(weather_icons['sunrise']), font = fontForecast, fill = 0)
    draw_black.text((300, current_outdoor_temp_y+10), sunset.astimezone(localtimezone).strftime("%H:%M",), font = fontSun, fill = 0)
    draw_black.text((270, current_outdoor_temp_y+10), unquote(weather_icons['sunset']), font = fontForecast, fill = 0)

  max_y = display_height - 80
  y = 30
  date = now
  dateutc = datetime(now.year, now.month, now.day, 0,0,0,0, timezone.utc) # FIXME: make timezone naive

  for i in range(7):

    if y > max_y:
      break

    # draw day and forecast
    if i != 0:
      draw_black.text((10, y), date.strftime("%A %-d/%-m"), font = fontDate, fill = 0)
      if weather_data is not None:
        draw_black.text((280, y), unquote(weather_icons[weather_data['attributes']['forecast'][i]['condition']]), font = fontForecast, fill = 0)
        draw_black.text((320, y), str(weather_data['attributes']['forecast'][i]['temperature']) + ' °C' , font = fontSun, fill = 0)
    
    y+=30

    # draw events for the day
    if events is not None:
      for ev in events:
        eventStart = ev.datetimestart
        eventEnd = ev.datetimeend
        if y > max_y:
          break
        if not ev.date == date.date() and not eventStart <= dateutc < eventEnd:
          continue
        if not ev.allday:
          row = "{} {}".format(eventStart.astimezone(localtimezone).strftime("%H:%M",), ev.summary)
        else:
          row = ev.summary
        if i == 0:
          font = fontEventToday
        else:
          font = fontEvent
        draw_black.text((10,y), row, font = font, fill = 0)
        y += 24

    # increment
    y += 12
    date = date + timedelta(days=1)
    dateutc = dateutc + timedelta(days=1)

  return black_image
