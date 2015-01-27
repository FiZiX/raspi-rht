import cherrypy

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        # Get home path
        home = expanduser("~")
        # Read settings and status from XML file
        xmlPath = home+"/raspi-rht/control.xml"
        tree = ET.parse(xmlPath)
        root = tree.getroot()
        settingsXML = root.find("settings")
        statusXML = root.find("status")
        enabled = settingsXML.find("enabled").text
        nextStart = statusXML.find("nextScheduledStart").text
        nextStop = statusXML.find("nextScheduledStop").text
        rh = statusXML.find("lastRH").text
        temp = statusXML.find("lastTemp").text
        currentDateTime = statusXML.find("lastUpdate").text
        friendlyStatus = statusXML.find("lastStatus").text
        lastDiscovery = statusXML.find("lastDiscovery").text
        return "Temp: "+temp+"\tRH: "+rh+"\nEnabled: "+enabled

if __name__ == '__main__':
   cherrypy.config.update("server.conf")
   cherrypy.quickstart(HelloWorld())

