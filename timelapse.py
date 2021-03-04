#!/usr/bin/env python3

'''
timelapse.py

This script is used to take pictures with a raspberry pi
camera. It is designed to be called from a crontab file,
and the pictures later stiched together to make a
timelapse movie.

Jennifer Liddle <jennifer@jsquared.co.uk>
'''

import datetime
from time import sleep
from astral.sun import sun
from astral import LocationInfo

import picamera
import sys
import getopt

destDir = '.'
nightMode = False

def displayHelp():
    print('timelapse.py: take photographs used for timelapse photography')
    print('Usage:  timelapse.py [options]')
    print('Where [options] are one or more of:')
    print(' -h  --help      Display this help message and exit.')
    print(' -d  --destDir   Directory to store pictures.')
    print('                 Default is the current directory.')
    print(' -n  --night     Include pictures taken at night.')
    print('                 Default is not to take pictures')
    print('                 between the hours of dusk to dawn')
    print('')
try:
    opts, args = getopt.getopt(sys.argv[1:],"hd:n",["destdir=","night"])
except getopt.GetoptError:
    displayHelp()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '-?', '--help'):
        displayHelp()
        sys.exit(0)

    if opt in ('-d', '--destDir'):
        destDir = arg

    if opt in ('-n', '--night'):
        nightMode = True

now = datetime.datetime.now()
filename = destDir + '/' + now.strftime("%Y%m%d_%H%M%S") + '.jpg'

# Find dusk and dawn
city = LocationInfo("London", "England", "Europe/London", 51.5, -0.116)
s = sun(city.observer, date=datetime.date.today())

dusk = s['dusk']
dawn = s['dawn']
now = datetime.datetime.now(dawn.tzinfo)

# is it dark?
dark = (now < dawn) or (now > dusk)

if not dark or nightMode:
    c = picamera.PiCamera()
    sleep(5)
    c.capture(filename)
    c.close()

