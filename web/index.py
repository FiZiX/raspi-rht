#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import cherrypy
import xml.etree.cElementTree as ET
from datetime import datetime

path   = os.path.abspath(os.path.dirname(__file__))
config = {
  'global' : {
    'server.socket_host' : '0.0.0.0',
    'server.socket_port' : 8080,
    'server.thread_pool' : 4
  }
}

class raspiRHT(object):
    @cherrypy.expose
    def index(self):
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
        
        # Set input time format
        timeFormatIn = "%Y-%m-%d %H:%M:%S.%f"
        # Set output time format (24 hour)
        #timeFormatOut = "%H:%M %m/%d/%Y"
        # Set output time format (12 hour)
        timeFormatOut = "%I:%M%p %m/%d/%Y"
        
        # Convert to dateTime object
        s = datetime.strptime(nextStart, timeFormatIn)
        # Convert to US date/time format
        nextStart = s.strftime(timeFormatOut)
        # Convert to dateTime object
        s = datetime.strptime(nextStop, timeFormatIn)
        # Convert to US date/time format
        nextStop = s.strftime(timeFormatOut)
        # Convert to dateTime object
        s = datetime.strptime(lastStart, timeFormatIn)
        # Convert to US date/time format
        lastStart = s.strftime(timeFormatOut)
        # Convert to dateTime object
        s = datetime.strptime(lastStop, timeFormatIn)
        # Convert to US date/time format
        lastStop = s.strftime(timeFormatOut)
        # Convert to dateTime object
        s = datetime.strptime(lastUpdate, timeFormatIn)
        # Convert to US date/time format
        lastUpdate = s.strftime(timeFormatOut)
        # Convert to dateTime object
        s = datetime.strptime(lastDiscovery, timeFormatIn)
        # Convert to US date/time format
        lastDiscovery = s.strftime(timeFormatOut)
        
        
        # Put HTML file in string
        with open ("index.html", "r") as myfile:
            html=myfile.read()
        
        # Replace key value pairs
        mapping = [ ('{rh}', rh), ('{temp}', temp), ('{enabled}', enabled), ('{friendlyStatus}', friendlyStatus), ('{nextStart}', nextStart), ('{nextStop}', nextStop), ('{lastStart}', lastStart), ('{lastStop}', lastStop), ('{lastUpdate}', lastUpdate), ('{lastDiscovery}', lastDiscovery) ]
        for k, v in mapping:
            html = html.replace(k, v)
        
        return html

cherrypy.tree.mount(raspiRHT(), '/', config)

if __name__ == '__main__':
  cherrypy.engine.signals.subscribe()
  cherrypy.engine.start()
  cherrypy.engine.block()
