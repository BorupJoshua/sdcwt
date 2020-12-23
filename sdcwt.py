# This Python code will grab the wait times of specific rides from Silver Dollar City's api.
import json
import urllib.request
import time
import datetime
import neopixel
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

#-- CONFIG
UPDATE_DELAY = 0.25 # In minutes

CLOSED_UPDATE_DELAY = 0.25 # In minutes

# Turn on BUFFER_TIME before park opening and BUFFER_TIME after
BUFFER_TIME = 60 # In minutes

#RIDES WE WANT TO LOOK AT
RIDES = {
    "American Plunge", 
    "Electro Spin", 
    "Fire In The Hole",
    "FireFall",
    "Flooded Mine",
    "Giant Swing",
    "Mystic River Falls",
    "Outlaw Run",
    "Powder Keg",
    "Thunderation",
    "Time Traveler",
    "Tom & Huck\'s River Blast",
    "Wildfire"
    }

# In order of the RIDES, set the position of the led. 
LED_NUM = [1,2,3,4,5,6,7,8,9,10,11,12,13]

# Brightness of the leds
BRIGHTNESS = 0.25

# Color codes in Green,Red,Blue
COLOR_NO_WAIT_OR_OPEN = (100,15,0)
COLOR_15_TO_45_WAIT = (100,125,0)
COLOR_45_TO_75_WAIT = (50,250,0)
COLOR_75_TO_120_WAIT = (0,255,0)
COLOR_120_OR_HIGHER = (0,125,125)
COLOR_CLOSED = (0,0,50)

#Pin on the board
LED_PIN = board.D18

#Total pins on your string
LED_COUNT = 50

#WAIT TIME JSON
WAIT_TIME_URL = "http://pulse.hfecorp.com/api/waitTimes/2"

#PARK HOURS JSON
DATE_TIME_URL = "https://www.silverdollarcity.com/api/cxa/DailySchedule/GetDailySchedule?did={687E9C32-0FAC-4F7E-A48B-5676DC4242D3}&hsi=True&dt=False&sd="

# SCREEN CONFIG
WIDTH = 128
HEIGHT = 64
BORDER = 1

#-- END CONFIG

def lookupColor(waitTime):
    if waitTime <= 15:
        return COLOR_NO_WAIT_OR_OPEN
    if waitTime > 15 and waitTime < 45:
        return COLOR_15_TO_45_WAIT
    if waitTime >= 45 and waitTime < 75:
        return COLOR_45_TO_75_WAIT
    if waitTime     >= 75 and waitTime < 120:
        return COLOR_75_TO_120_WAIT
    else:
        return COLOR_120_OR_HIGHER


print("Running initalizations")

waitTimes = []

for i in range(len(RIDES)):
    waitTimes.append(0)

lastDate = datetime.datetime(2000, 1, 1)
parkOpen = None
parkClose = None
updateRate = UPDATE_DELAY
cleanUp = False
iterNum = 0
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, pixel_order = neopixel.GRB, brightness = BRIGHTNESS, auto_write = True)

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Generate screen
# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)


# Load default font.
font = ImageFont.load_default()

# Draw a white background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Draw a smaller inner rectangle

draw.rectangle(
    (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
    outline=0,
    fill=0,
)


now = datetime.datetime.now()

text6 = "Updated: " + now.strftime("%I:%M%p")
(font6_width, font6_height) = font.getsize(text6)
draw.text(
    (oled.width//2 - font6_width//2, oled.height - (font6_height)),
    text6,
    font=font,
    fill=255,
    anchor="mm",
)

oled.image(image)
oled.show()
while True:
    print("Updating information!")

    # Check the day, if set date is not todays date then update date then update park hours
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    if lastDate != today:
        print("Updating today's date!")
        # Set the last known date as today
        lastDate = today

        # Combine the perm date api ur  l and today's date
        loadURL = DATE_TIME_URL + today
        
        # fetch the json file data from the url
        apiDatesData = urllib.request.urlopen(DATE_TIME_URL).read().decode()

        # take the json file data and actually format it into a json object
        jsonDateObj = json.loads(apiDatesData)

        # parse the json object to get the park opening and closings
        # This is the most likely thing to mess up if SDC ever changes their date formatting.
        parkOpenRaw = jsonDateObj['dates'][0]['parks'][0]['parkOpen']
        parkCloseRaw = jsonDateObj['dates'][0]['parks'][0]['parkClose']

        # Convert the string into date time objects
        parkOpen = datetime.datetime.strptime(parkOpenRaw, '%m-%d-%Y %I:%M:%S %p')
        parkClose = datetime.datetime.strptime(parkCloseRaw, '%m-%d-%Y %I:%M:%S %p')

        draw.rectangle(
            ([(1,1),(126,55)]),
            outline=0,
            fill=0,
        )

        text1 = now.strftime("%B %d, %Y")

        (font_width, font_height) = font.getsize(text1)
        draw.text(
            (oled.width // 2 - font_width // 2, font_height // 2-3),
            text1,
            font=font,
            fill=255,
            anchor="mm",
        )


        print("Today is ", today)
        if (parkClose is not None):
            print("The park opens at ", parkOpen)
            print("The park closes at ", parkClose)
            updateRate = UPDATE_DELAY
            
            # Update screen
            text2 = "Opens"
            text3 = "Closes"
            text4 = parkOpen.strftime('%I:%M%p')
            text5 = parkClose.strftime('%I:%M%p')
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
            print("Looks like there's no hours posted today, assuming it's closed!")

            text7 = 'Closed Today'
            (font7_width, font7_height) = font.getsize(text7)
            draw.text(
                (oled.width//2 - font7_width//2, 28),
                'Closed Today',
                font=font,
                fill=255,
                anchor="mm",
            )


        draw.line([(0,15),(128,15)], fill=1, width=2)

        draw.line([(0,53),(128,53)], fill=1, width=1)

        

    # end if


    # If the parkOpen is not null then continue, else we change the update check to be every hour.
    if parkOpen is not None:

        print("The park is NOT closed today!")

        #Set our update rate to the one we defined
        updateRate = UPDATE_DELAY

        # Create a now object of the current time.
        now = datetime.datetime.now()
        print(now)
        # If Time is 1 hour (or buffer time) before opening or 1 hours (or buffer time) after closing and this is new to us, turn off all the leds
        if (now < (parkOpen - datetime.timedelta(minutes=BUFFER_TIME)) or now > (parkClose + datetime.timedelta(minutes=BUFFER_TIME))) and cleanUp is False:
            cleanUp = True
            if (now > (parkClose + datetime.timedelta(minutes=BUFFER_TIME))):
                updateRate = CLOSED_UPDATE_DELAY
            print("Looks like we're closed right now, let's turn off the leds!")

            pixels.fill((0,0,0))

            # turn off all LEDs
        
        

        # else update the wait times
        elif (now >= (parkOpen - datetime.timedelta(minutes=BUFFER_TIME)) and now <= (parkClose + datetime.timedelta(minutes=BUFFER_TIME))):
            print("We're open! Let's update the rides wait times!")
            
            # Grab json from sdc's api
            apiwaitData = urllib.request.urlopen(WAIT_TIME_URL).read().decode()
            waitObj = json.loads(apiwaitData)


            # Tell us we need to clean up if the park closes
            cleanup = False

            # For every entry in the json file
            for i in waitObj:

                # if the current entry in the file is one we listed
                if i['rideName'] in RIDES:
                    print(i['rideName'])
                    pixels[LED_NUM[iterNum]] = (255,255,255)
                    # If the waitTime is null, it's probably closed
                    if (i['operationStatus'] != "OPEN" ):
                        print('Closed')
                        # -1 = closed
                        waitTimes[iterNum] = -1
                        pixels[LED_NUM[iterNum]] = COLOR_CLOSED
                    else:
                        if i['waitTime'] is None:
                            print("Less than 15 minutes")
                            waitTimes[iterNum] = 5
                            pixels[LED_NUM[iterNum]] = lookupColor(5)
                        else:
                            print(i['waitTime'])
                            waitTimes[iterNum] = i['waitTime']
                            pixels[LED_NUM[iterNum]] = lookupColor(i['waitTime'])
                    iterNum = iterNum + 1

            # Reset our iter Object
            iterNum = 0

            # Update leds here
    else:
        print("Looks like the park isn't open today!  Let's make our updates slower!")
        #Since the park is closed, let's lower our update rate to the closed update rate
        updateRate = CLOSED_UPDATE_DELAY

        if cleanUp is False:
            # Turn off the leds as well
            print('Turn off lights')
            pixels.fill((0,0,0))

    now = datetime.datetime.now()

    draw.rectangle(
        (2,54,124,63),
        outline=0,
        fill=0,
    )

    text6 = "Updated: " + now.strftime("%I:%M%p")
    (font6_width, font6_height) = font.getsize(text6)
    draw.text(
        (oled.width//2 - font6_width//2, oled.height - (font6_height)),
        text6,
        font=font,
        fill=255,
        anchor="mm",
    )
    oled.image(image)
    oled.show()

    print("I'm sleepy, I'll see you in 5 minutes")
    time.sleep(60 * updateRate)