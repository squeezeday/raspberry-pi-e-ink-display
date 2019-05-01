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

  sensor_data = json.loads(content)

  baseImage = Image.new('1', (display_width, display_height), 255)

  draw = ImageDraw.Draw(baseImage)

  # Clock

  clockFontLarge = ImageFont.truetype('SourceSansPro-Bold.ttf', 110)

  now = datetime.datetime.now()

  draw.text((200, 100), now.strftime('%H:%M'), font = clockFontLarge, fill = 0)

  # Weather stuff

  draw.rectangle([(0, 240), (display_width, 242)], fill = 0)

  iconFontLarge = ImageFont.truetype('materialdesignicons-webfont.ttf', 48)
  iconFontSmall = ImageFont.truetype('materialdesignicons-webfont.ttf', 32)

  weatherFontLarge = ImageFont.truetype('SourceSansPro-Bold.ttf', 36)
  weatherFontMedium = ImageFont.truetype('SourceSansPro-Bold.ttf', 24)
  weatherFontSmall = ImageFont.truetype('SourceSansPro-Regular.ttf', 16)

  draw.text((250, 255), unquote(weather_icons[sensor_data['state']]), font = iconFontLarge, fill = 0)

  draw.text((310, 252), str(sensor_data['attributes']['temperature']) + ' °C', font = weatherFontLarge, fill = 0)

  draw.rectangle([(0, 313), (display_width, 314)], fill = 0)

  for i in range(3):

    date = datetime.datetime.strptime(sensor_data['attributes']['forecast'][i]['datetime'], '%Y-%m-%dT%H:%M:%S')

    draw.text(((213*i)+10, 320), date.strftime("%A %-d.%-m."), font = weatherFontSmall, fill = 0)

    draw.text(((213*i)+10, 343), unquote(weather_icons[sensor_data['attributes']['forecast'][i]['condition']]), font = iconFontSmall, fill = 0)

    draw.text(((213*i)+50, 341), str(sensor_data['attributes']['forecast'][i]['temperature']) + ' °C' , font = weatherFontMedium, fill = 0)

    if i < 2:
      draw.rectangle([((213*i)+ 210, 320), ((213*i)+ 211, 380)], fill = 0)

  return baseImage
