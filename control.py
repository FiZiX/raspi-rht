# Imports
import subprocess
from os.path import expanduser
from ouimeaux.environment import Environment

# Set the target humidity level
targetRH = 45
# Set the tolerance (+/-) for humidity level
tolerance = 2

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

# Status remains at 4 if no conditions are matched
status = 4

# Check if humidifier is out of water
if isHumidifierOutOfWater():
    status = 2
# Check if humidifier is running
elif isHumidifierRunning():
    status = 1
# Check if humidifier is stopped
elif isHumidifierStopped():
    status = 0

# If status is still 4, there's an issue reading the status
if status == 4:
    # Exit with error status
    raise SystemExit(1)

# Check if we need to start or stop humidifier
if rh <= minRH && status == 0:
    startHumidifier()
elif rh >= maxRH && status == 1:
    stopHumidifier()
