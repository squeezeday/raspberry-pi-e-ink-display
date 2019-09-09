from draw import create_image
from PIL import Image
from waveshare_epd import epd7in5

black_image = create_image()

epd = epd7in5.EPD()
print("Init epd7in5..")
epd.init()

print("Clearing...")
epd.Clear()

print("Display image")
epd.display(epd.getbuffer(black_image))

epd.sleep()
print("Done")