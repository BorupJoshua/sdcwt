"""
This demo will fill the screen with white, draw a black box on top
and then print Hello World! in the center of the display

This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
"""

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import datetime
import time


# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 1

parkOpen = False

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a white background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Draw a smaller inner rectangle

draw.rectangle(
    (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
    outline=0,
    fill=0,
)

# Load default font.
font = ImageFont.load_default()

# Draw Some Text
now = datetime.datetime.now()
text = now.strftime("%B %d, %Y")
text2 = "Opens"
text3 = "Closes"
text4 = "10:00am"
text5 = "09:00pm"
text6 = "Updated: " + now.strftime("%I:%M%p")
(font_width, font_height) = font.getsize(text)
draw.text(
    (oled.width // 2 - font_width // 2, font_height // 2-3),
    text,
    font=font,
    fill=255,
    anchor="mm",
)



if parkOpen == True:

    comp_height = font_height + 6

    (font2_width, font2_height) = font.getsize(text2)
    (font3_width, font3_height) = font.getsize(text3)
    (font4_width, font4_height) = font.getsize(text4)
    (font5_width, font5_height) = font.getsize(text5)
    draw.text(
        (18, (font2_height // 2) + comp_height),
        text2,
        font=font,
        fill=255,
        anchor="mm",
    )
    draw.text(
        (oled.width - font5_width-8, (font2_height // 2) + comp_height),
        text3,
        font=font,
        fill=255,
        anchor="mm",
    )

    comp_height = comp_height + 2 + font2_height

    draw.text( 
        (12, (font2_height // 2) + comp_height),
        text4,
        font=font,
        fill=255,
        anchor="mm",
    )
    draw.text(
        (oled.width - font5_width-10, (font2_height // 2) + comp_height),
        text5,
        font=font,
        fill=255,
        anchor="mm",
    )

    draw.line([(63,15),(63,53)], fill=1, width=1)

else:
    text7 = 'Closed Today'
    (font7_width, font7_height) = font.getsize(text7)
    draw.text(
        (oled.width//2 - font7_width//2, 30),
        'Closed Today',
        font=font,
        fill=255,
        anchor="mm",
    )

(font6_width, font6_height) = font.getsize(text6)
draw.text(
    (oled.width//2 - font6_width//2, oled.height - (font6_height)),
    text6,
    font=font,
    fill=255,
    anchor="mm",
)


draw.line([(0,15),(128,15)], fill=1, width=2)

draw.line([(0,53),(128,53)], fill=1, width=1)


# Display image
oled.image(image)
oled.show()
