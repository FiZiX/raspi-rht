import subprocess
from os.path import expanduser
# Get home path
home = expanduser("~")
# Run program to get temp and humidity from sensor
p = subprocess.Popen(["sudo", home+"/raspi-rht/./th_2"], stdout=subprocess.PIPE)
output, err = p.communicate()
# Split the output into separate variables
temp, rh = output.split()
print "Temp: "+temp+"\tRH: "+rh
