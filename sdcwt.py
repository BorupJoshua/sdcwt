# This Python code will grab the wait times of specific rides from Silver Dollar City's api.
import json
import urllib.request
import time
import datetime
import neopixel
import board

#-- CONFIG
UPDATE_DELAY = 5 # In minutes

CLOSED_UPDATE_DELAY = 60 # In minutes

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

        print("Today is ", today)
        if (parkClose is not None):
            print("The park opens at ", parkOpen)
            print("The park closes at ", parkClose)
            updateRate = UPDATE_DELAY
        else:
            print("Looks like there's no hours posted today, assuming it's closed!")

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

    print("I'm sleepy, I'll see you in 5 minutes")
    time.sleep(60 * updateRate)