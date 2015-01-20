# Imports
import subprocess
from os.path import expanduser
from ouimeaux.environment import Environment
from datetime import datetime, timedelta
import xml.etree.cElementTree as ET

# Functions
def connectToWeMo(switchName):
    "Connects to the WeMo switch"
    env = Environment()
    env.start()
    return env.get_switch(switchName)

def isHumidifierRunning(switch):
    "Checks if WeMo switch is on"
    if switch.basicevent.GetBinaryState()['BinaryState'] == '1':
        return True
    else:
        return False

def isHumidifierStopped(switch):
    "Checks if WeMo switch is off"
    if switch.basicevent.GetBinaryState()['BinaryState'] == '0':
        return True
    else:
        return False

def isHumidifierOutOfWater(switch):
    "Checks if WeMo energy usage is low"
    # Extract current energy usage in mW
    usage = switch.insight.GetInsightParams()['InsightParams'].split("|")[7]
    # Convert to watts
    usage = int(usage) / 1000
    # If watts is less than 10, it's out of water, unplugged, or turned off
    if usage < 10:
        return True
    else:
        return False

def sendOutOfWaterAlert():
    "Send an alert about humidifier being out of water"
    # TODO
    return

def startHumidifier(switch):
    "Turns the WeMo switch on"
    switch.basicevent.SetBinaryState(BinaryState=1)
    return

def stopHumidifier(switch):
    "Turns the WeMo switch off"
    switch.basicevent.SetBinaryState(BinaryState=0)
    return

# Get home path
home = expanduser("~")    
# Read settings from XML file
xmlPath = home+"/raspi-rht/control.xml"
tree = ET.parse(xmlPath)
root = tree.getroot()
settings = root.find("settings")

# Check if script is enabled. Quit if not.
enabled = settings.find("enabled").text
if enabled != "True":
    raise SystemExit(1)

# Get the target humidity level
targetRH = int(settings.find("targetRH").text)
# Get the tolerance for humidity level
tolerance = int(settings.find("tolerance").text)
# Get time of day (24 hour format) in which the humidifier should start running
startTime = settings.find("startTime").text
# Get how many hours it should run and convert to seconds
runHours = int(settings.find("runHours").text)
# Get "friendly" name of WeMo Switch
switchName = settings.find("switchName").text

# Calculate maximum humidity
maxRH = targetRH + tolerance
# Calculate minimum humidity
minRH = targetRH - tolerance

# Run program to get temp and humidity from sensor
p = subprocess.Popen(["sudo", home+"/raspi-rht/./th_2"], stdout=subprocess.PIPE)
output, err = p.communicate()

# Split the output into separate variables
temp, rh = output.split()
print "Temp: "+temp+"\tRH: "+rh

# Make them floats
temp = float(temp)
rh = float(rh)

# Connect to WeMo Switch
switch = connectToWeMo(switchName)

# Status remains at 4 if no conditions are matched
status = 4

# Check if humidifier is running
if isHumidifierRunning(switch):
    # Check if humidifier is out of water
    if isHumidifierOutOfWater(switch):
        status = 2
    else:
        status = 1
# Check if humidifier is stopped
elif isHumidifierStopped(switch):
    status = 0

print "Status = "+str(status)

# If status is still 4, there's an issue reading the status
if status == 4:
    # Exit with error status
    raise SystemExit(1)

# Set time format
timeFormat = "%Y-%m-%d %H:%M:%S.%f"

status = root.find("status")

# Get current date and time as datetime object
currentDateTime = datetime.now()

# Get next time humidifier should start
nextStart = status.find("nextScheduledStart").text

# If nextStart is None, assign to next start time on today's date
if nextStart is None:
    nextStart = currentDateTime.strftime("%Y-%m-%d")+" "+startTime+".000000"

# Convert nextStart into datetime object
nextStart = datetime.strptime(nextStart, timeFormat)

# Get next time humidifier should stop
nextStop = status.find("nextScheduledStop").text

# If nextStop is None, make it nextStart + runHours
if nextStop is None:
    nextStop = nextStart + timedelta(hours=runHours)
else:
    # Convert nextStop into datetime object
    nextStop = datetime.strptime(nextStop, timeFormat)

# Check if start and stop times need to be updated
if currentDateTime > nextStop:
    nextStart = currentDateTime.strftime("%Y-%m-%d")+" "+startTime+".000000"
    # Convert nextStart into datetime object
    nextStart = datetime.strptime(nextStart, timeFormat)
    if currentDateTime > nextStart:
        # Add 24 hours to nextStart
        nextStart = nextStart + timedelta(hours=24)
    nextStop = nextStart + timedelta(hours=runHours)

# Start or stop humidifier based on time and relative humidity
if status == 2:
    sendOutOfWaterAlert()
    finalStatus = "Out of Water"
elif status == 0 and rh <= minRH and currentDateTime >= nextStart:
    startHumidifier(switch)
    finalStatus = "Running"
    status.find("startedDateTime").text = str(currentDateTime)
elif status == 1 and (rh >= maxRH or currentDateTime < nextStart):
    stopHumidifier(switch)
    finalStatus = "Not Running"
    status.find("stoppedDateTime").text = str(currentDateTime)

# Update status in XML file
status.find("lastRH").text = str(rh)
status.find("lastTemp").text = str(temp)
status.find("lastUpdate").text = str(currentDateTime)
status.find("lastStatus").text = str(finalStatus)
status.find("nextScheduledStart").text = str(nextStart)
status.find("nextScheduledStop").text = str(nextSttop)
tree.write(xmlPath)
