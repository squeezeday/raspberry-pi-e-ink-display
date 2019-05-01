from draw import create_image
from PIL import Image
import epd7in5b

blackimage = create_image()

redimage = Image.new('1', (epd7in5b.EPD_WIDTH, epd7in5b.EPD_HEIGHT), 255) 

epd = epd7in5b.EPD()
epd.init()

# print("Clearing...")
# epd.Clear(0xFF)

epd.display(epd.getbuffer(blackimage), epd.getbuffer(redimage))

epd.sleep()
