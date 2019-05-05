from draw import create_image
from PIL import ImageChops, ImageOps

black_image, red_image = create_image()

combined_image = ImageChops.logical_and(black_image, red_image)

combined_image.show()