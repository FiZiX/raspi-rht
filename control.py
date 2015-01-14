# Imports
import subprocess
from os.path import expanduser
from ouimeaux.environment import Environment

# Set the target humidity level
targetRH = 45
# Set the tolerance (+/-) for humidity level
tolerance = 2
# Set "friendly" name of WeMo Switch
switchName = "WeMo Insight"

# Calculate maximum humidity
maxRH = targetRG + tolerance
# Calculate minimum humidity
minRH = targetRG - tolerance

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

# Check if we need to start or stop humidifier
# if rh <= minRH && status == 0:
    # startHumidifier()
# elif rh >= maxRH && status == 1:
    # stopHumidifier()

def connectToWeMo(switchName):
    "Connects to the WeMo switch"
    env = Environment()
    env.start()
    return env.get_switch(switchName)

def isHumidifierRunning(switch):
    "Checks if WeMo switch is on"
    if switch.basicevent.GetBinaryState()['BinaryState'] == '1':
        print true;
    else:
        return false

def isHumidifierStopped(switch):
    "Checks if WeMo switch is off"
    if switch.basicevent.GetBinaryState()['BinaryState'] == '0':
        return true
    else:
        return false

def isHumidifierOutOfWater(switch):
    "Checks if WeMo energy usage is low"
    # Extract current energy usage in mW
    usage = switch.insight.GetInsightParams()['InsightParams'].split("|")[7]
    # Convert to watts
    usage = int(usage) / 1000
    # If watts is less than 10, it's out of water, unplugged, or turned off
    if usage < 10:
        return true
    else:
        return false
