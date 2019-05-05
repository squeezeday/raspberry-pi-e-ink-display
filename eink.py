from draw import create_image
from PIL import Image
import epd7in5b

black_image, red_image = create_image()

epd = epd7in5b.EPD()
epd.init()

# print("Clearing...")
# epd.Clear(0xFF)

epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))

epd.sleep()
