# Imports
import subprocess
from os.path import expanduser
from ouimeaux.environment import Environment

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

# Set the target humidity level
targetRH = 43
# Set the tolerance (+/-) for humidity level
tolerance = 2
# Set "friendly" name of WeMo Switch
switchName = "WeMo Insight"

# Calculate maximum humidity
maxRH = targetRH + tolerance
# Calculate minimum humidity
minRH = targetRH - tolerance

# Get home path
home = expanduser("~")

# Run program to get temp and humidity from sensor
p = subprocess.Popen(["sudo", home+"/raspi-rht/./th_2"], stdout=subprocess.PIPE)
output, err = p.communicate()

# Split the output into separate variables
temp, rh = output.split()
print "Temp: "+temp+"\tRH: "+rh

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

# Start or stop humidifier based on relative humidity
if status == 2:
    sendOutOfWaterAlert()
elif rh <= minRH && status == 0:
    startHumidifier(switch)
elif rh >= maxRH && status == 1:
    stopHumidifier(switch)
