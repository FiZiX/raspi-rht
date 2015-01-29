import cherrypy
from os.path import expanduser
import xml.etree.cElementTree as ET

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        # Get home path
        home = expanduser("~")
        # Read settings and status from XML file
        xmlPath = "../control.xml"
        tree = ET.parse(xmlPath)
        root = tree.getroot()
        settingsXML = root.find("settings")
        statusXML = root.find("status")
        enabled = settingsXML.find("enabled").text
        nextStart = statusXML.find("nextScheduledStart").text
        nextStop = statusXML.find("nextScheduledStop").text
        lastStart = statusXML.find("startedDateTime").text
        lastStop = statusXML.find("stoppedDateTime").text
        rh = statusXML.find("lastRH").text
        temp = statusXML.find("lastTemp").text
        lastUpdate = statusXML.find("lastUpdate").text
        friendlyStatus = statusXML.find("lastStatus").text
        lastDiscovery = statusXML.find("lastDiscovery").text
        return "Temp: "+temp+"\tRH: "+rh+"\nEnabled: "+enabled

if __name__ == '__main__':
   cherrypy.config.update("server.conf")
   cherrypy.quickstart(HelloWorld())
