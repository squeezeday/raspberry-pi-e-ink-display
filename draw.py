from PIL import Image, ImageDraw, ImageFont
from urllib.request import Request, urlopen
from urllib.parse import quote, unquote
import json
import datetime
import os

from dotenv import load_dotenv
load_dotenv()

import locale
locale.setlocale(locale.LC_ALL, os.getenv('LOCALE'))

home_assistant_base_url = os.getenv('HOME_ASSISTANT_BASE_URL')
home_assistant_access_token = os.getenv('HOME_ASSISTANT_ACCESS_TOKEN')

display_width = int(os.getenv('DISPLAY_WIDTH'))
display_height = int(os.getenv('DISPLAY_HEIGHT'))

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
  'windy': '%EF%96%9D'
}

def create_image():

  req = Request(home_assistant_base_url + 'states/weather.dark_sky')
  req.add_header('Authorization', 'Bearer ' + home_assistant_access_token)
  content = urlopen(req).read()

  sensor_data = json.loads(content.decode("utf-8"))

  black_image = Image.new('1', (display_width, display_height), 255)
  red_image = Image.new('1', (display_width, display_height), 255) 

  draw_black = ImageDraw.Draw(black_image)
  draw_red = ImageDraw.Draw(red_image)

  # Date & calendar

  dateFontLarge = ImageFont.truetype('SourceSansPro-Bold.ttf', 60)
  dateFontSmall = ImageFont.truetype('SourceSansPro-Bold.ttf', 34)

  now = datetime.datetime.now()

  msg = now.strftime('%A - %-d.%-m.')

  text_w, text_h = draw_black.textsize(msg, font = dateFontLarge)

  draw_black.text(((display_width-text_w)/2, 10), msg, font = dateFontLarge, fill = 0)

  req = Request(home_assistant_base_url + 'states/' + os.getenv('CALENDAR'))
  req.add_header('Authorization', 'Bearer ' + home_assistant_access_token)
  content = urlopen(req).read()

  calendar_data = json.loads(content.decode("utf-8"))

  date = datetime.datetime.strptime(calendar_data['attributes']['start_time'], '%Y-%m-%d %H:%M:%S')

  msg = date.strftime("%-d.%-m.") + " " + calendar_data['attributes']['message']

  text_w, text_h = draw_black.textsize(msg, font = dateFontSmall)

  draw_black.text(((display_width-text_w)/2, 100), msg, font = dateFontSmall, fill = 0)

  # Weather stuff

  draw_black.rectangle([(0, 190), (display_width, 192)], fill = 0)

  iconFontLarge = ImageFont.truetype('materialdesignicons-webfont.ttf', 48)
  iconFontSmall = ImageFont.truetype('materialdesignicons-webfont.ttf', 32)

  weatherFontLarge = ImageFont.truetype('SourceSansPro-Bold.ttf', 40)
  weatherFontMedium = ImageFont.truetype('SourceSansPro-Bold.ttf', 24)
  weatherFontSmall = ImageFont.truetype('SourceSansPro-Regular.ttf', 16)

  line_w, line_h = draw_black.textsize(unquote(weather_icons[sensor_data['state']]), font = iconFontLarge)

  text_w, text_h = draw_black.textsize(str(sensor_data['attributes']['temperature']) + ' °C', font = weatherFontLarge)

  offset_x = (display_width - (line_w + text_w) + 10) / 2

  draw_red.text((offset_x, 215), unquote(weather_icons[sensor_data['state']]), font = iconFontLarge, fill = 0)

  draw_black.text((offset_x + 60, 212), str(sensor_data['attributes']['temperature']) + ' °C', font = weatherFontLarge, fill = 0)

  draw_black.rectangle([(0, 283), (display_width, 284)], fill = 0)

  offset_x = round(display_width / 3)

  for i in range(3):

    date = datetime.datetime.strptime(sensor_data['attributes']['forecast'][i]['datetime'], '%Y-%m-%dT%H:%M:%S')

    draw_black.text(((offset_x*i)+10, 305), date.strftime("%A %-d.%-m."), font = weatherFontSmall, fill = 0)

    draw_red.text(((offset_x*i)+10, 328), unquote(weather_icons[sensor_data['attributes']['forecast'][i]['condition']]), font = iconFontSmall, fill = 0)

    draw_black.text(((offset_x*i)+50, 326), str(sensor_data['attributes']['forecast'][i]['temperature']) + ' °C' , font = weatherFontMedium, fill = 0)

    if i < 2:
      draw_black.rectangle([((offset_x*i)+ offset_x - 3, 290), ((offset_x*i)+ offset_x - 2, 380)], fill = 0)

  return black_image, red_image
