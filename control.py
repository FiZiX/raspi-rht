# Imports
import subprocess
from os.path import expanduser
from ouimeaux.environment import Environment
from datetime import datetime, timedelta
import xml.etree.cElementTree as ET

# Functions
def startWeMoEnvironment():
    "Starts the WeMo environment"
    env = Environment()
    env.start()
    return env

def discoverWeMoDevices(env):
    "Discover WeMo devices"
    env.discover(seconds=3)
    return

def connectToWeMo(env, switchName):
    "Connects to the WeMo switch"
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
settingsXML = root.find("settings")
statusXML = root.find("status")

# Check if script is enabled. Quit if not.
enabled = settingsXML.find("enabled").text
if enabled != "True":
    raise SystemExit(1)

# Get the target humidity level
targetRH = int(settingsXML.find("targetRH").text)
# Get the tolerance for humidity level
tolerance = int(settingsXML.find("tolerance").text)
# Get time of day (24 hour format) in which the humidifier should start running
startTime = settingsXML.find("startTime").text
# Get how many hours it should run and convert to seconds
runHours = int(settingsXML.find("runHours").text)
# Get "friendly" name of WeMo Switch
switchName = settingsXML.find("switchName").text

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

# Set time format
timeFormat = "%Y-%m-%d %H:%M:%S.%f"

# Get current date and time as datetime object
currentDateTime = datetime.now()

# Start WeMo environment
env = startWeMoEnvironment()

# Check the last time we ran a WeMo discovery cycle
lastDiscovery = statusXML.find("lastDiscovery").text

if lastDiscovery is not None:
    # Convert to datetime object
    lastDiscovery = datetime.strptime(lastDiscovery, timeFormat)

# Check if lastDiscovery is None or was more than 24 hours ago
if lastDiscovery is None or (lastDiscovery + timedelta(hours=24)) < currentDateTime:
    # Clear WeMo cache
    p = subprocess.Popen(["wemo", "clear"], stdout=subprocess.PIPE)
    p.communicate()
    # Rediscover devices
    discoverWeMoDevices(env)
    lastDiscovery = currentDateTime

# Connect to WeMo Switch
switch = connectToWeMo(env, switchName)

# Status remains at 4 if no conditions are matched
status = 4

# Check if humidifier is running
if isHumidifierRunning(switch):
    # Check if humidifier is out of water
    if isHumidifierOutOfWater(switch):
        status = 2
        friendlyStatus = "Out of Water"
    else:
        status = 1
        friendlyStatus = "Running"
# Check if humidifier is stopped
elif isHumidifierStopped(switch):
    status = 0
    friendlyStatus = "Not Running"

print "Status = "+str(status)

# If status is still 4, there's an issue reading the status
if status == 4:
    # Exit with error status
    raise SystemExit(1)

# Get next time humidifier should start
nextStart = statusXML.find("nextScheduledStart").text

# If nextStart is None, assign to next start time on today's date
if nextStart is None:
    nextStart = currentDateTime.strftime("%Y-%m-%d")+" "+startTime+".000001"

# Convert nextStart into datetime object
nextStart = datetime.strptime(nextStart, timeFormat)

# Get next time humidifier should stop
nextStop = statusXML.find("nextScheduledStop").text

# If nextStop is None, make it nextStart + runHours
if nextStop is None:
    nextStop = nextStart + timedelta(hours=runHours)
else:
    # Convert nextStop into datetime object
    nextStop = datetime.strptime(nextStop, timeFormat)

# Check if start and stop times need to be updated
if currentDateTime > nextStop:
    nextStart = currentDateTime.strftime("%Y-%m-%d")+" "+startTime+".000001"
    # Convert nextStart into datetime object
    nextStart = datetime.strptime(nextStart, timeFormat)
    if currentDateTime > nextStart:
        # Add 24 hours to nextStart
        nextStart = nextStart + timedelta(hours=24)
    nextStop = nextStart + timedelta(hours=runHours)

# Start or stop humidifier based on time and relative humidity
if status == 2:
    sendOutOfWaterAlert()
    friendlyStatus = "Out of Water"
elif status == 0 and rh <= minRH and currentDateTime >= nextStart:
    startHumidifier(switch)
    friendlyStatus = "Running"
    statusXML.find("startedDateTime").text = str(currentDateTime)
elif status == 1 and (rh >= maxRH or currentDateTime < nextStart):
    stopHumidifier(switch)
    friendlyStatus = "Not Running"
    statusXML.find("stoppedDateTime").text = str(currentDateTime)

# Update status in XML file
statusXML.find("nextScheduledStart").text = str(nextStart)
statusXML.find("nextScheduledStop").text = str(nextStop)
statusXML.find("lastRH").text = str(rh)
statusXML.find("lastTemp").text = str(temp)
statusXML.find("lastUpdate").text = str(currentDateTime)
statusXML.find("lastStatus").text = str(friendlyStatus)
statusXML.find("lastDiscovery").text = str(lastDiscovery)
tree.write(xmlPath)
