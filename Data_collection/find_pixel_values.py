import cv2
import numpy as np


import matplotlib.pyplot as plt

from rgb_to_cmyk import rgb_to_cmyk

# Assuming 'image_data' is a 2D numpy array representing your image

image = cv2.imread(r"C:\Users\softrobotslab\ArduinoMotors\TestData\image_1_1733282929.799722.jpg")
plt.imshow(image)

# Get 2 mouse clicks
coords = plt.ginput(10, timeout=10000)


# Print the coordinates
# print(coords)

# plt.show()
plt.close()

# Read the image
# image = cv2.imread('image.jpg')



# Access the pixel at coordinates (x, y)

for coord in coords:
    x = int(coord[0])
    y = int(coord[1])
    pixel_color = image[y, x]

    # Print the pixel color in BGR format
    print("Pixel color (BGR): ", pixel_color)
    # Convert BGR to RGB
    pixel_color_rgb = pixel_color[::-1] 
    print("Pixel color (RGB): ", pixel_color_rgb)
    
    print('cmyk: ', rgb_to_cmyk(pixel_color_rgb[0], pixel_color_rgb[1], pixel_color_rgb[2]), '\n')