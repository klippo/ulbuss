#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
import os
import getopt
import requests as r
import re
import HTMLParser


URL = 'http://mobil.ul.nu/stadsbuss/vemos2_web.dll/betatest/mhpl?hplnr=%s'
stationsFile = 'stations.txt'


def printUsage():
    print("Usage: %s [ options ]" % sys.argv[0])
    print("")
    print("Options:")
    print("         -[lgfh] [ --list ] [ --help ]")
    print("                      [ --get stationName ]")
    print("                      [ --fetch ]")
    print("")
    print("       --list (-l short option)")
    print("             Lists all fetched stations.")
    print("")
    print("       --help (-h short option)")
    print("             Shows this screen.")
    print("")
    print("       --get stationName (-g short option)")
    print("             Gets the current timetable for stationName provided.")
    print("")
    print("       --fetch (-f short option)")
    print("             Fetches all UL stations with ID between 700001 and 700611 and")
    print("             adds them to %s. This file is used when getting a timetable without" % stationsFile)
    print("             hammering their server.")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "g:hfl", ["get","help", "fetch"])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    opt = None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printUsage()
        elif opt in ("-g", "--get"):
            parseStations(arg)
        elif opt in ("-f", "--fetch"):
            fetchStations()
        elif opt in ("-l", "--list"):
            listStations()
    if not opt:
        printUsage()


def listStations():
    with open(stationsFile, 'r') as stations:
        print stations.read()

def parseStations(stationName):
    for station in stationName.split('|'):
        with open(stationsFile, 'r') as stations:
            for station in re.finditer('.*' + station + '.*', stations.read(), flags=re.MULTILINE):
                station = station.group(0).decode('utf8')
                stationName = station.split(',')[-1]
                stationId = station.split(',')[0]

                getStation(stationName, stationId)


def getStation(stationName, stationId):
    pars = HTMLParser.HTMLParser()
    response = r.get(URL % stationId)
    remove = [
        u'</div.*\n',
        u'<div.*\n',
        u'</b>.*\n',
        u', läge.*'
    ]
    print('Departures from %s' % stationName)
    for dst in re.finditer('[0-9].* mot.*\n.*\n.*\nom.*', response.text, flags=re.MULTILINE):
        destination = unicode(pars.unescape(dst.group(0).encode('utf8')))
        destination = re.sub('om', '\tom', destination)
        for val in remove:
            destination = re.sub(val, '', destination, flags=re.MULTILINE)
        print destination
    print('')


def fetchStations():
    print('Dont use this for now, use the provided %s' % stationsFile)
    sys.exit(0)
    pars = HTMLParser.HTMLParser()
    remove = [
        u'Avgångar från ',
        u' i Uppsala.*'
    ]
    if os.path.isfile(stationsFile):
        os.remove(stationsFile)
    for file in range(700001, 700612):
        file = str(file)

        with open('data/' +file + '.html', 'r') as infile:
        #response = r.get(URL % stationId)
            for match in re.finditer('Avg.* <', infile.read(), flags=re.MULTILINE):
            #for match in re.finditer('Avg.* <', response.text, flags=re.MULTILINE):
                station = unicode(pars.unescape(match.group(0).encode('utf8')))

                for val in remove:
                    station = re.sub(val, '', station, flags=re.MULTILINE)

                if len(station) > 0:
                    with open(stationsFile, "a") as myfile:
                            myfile.write(file + ',' + station.encode('utf8') + '\n')
    with open(stationsFile, 'r') as f:
        slength = len(f.readlines())
    print('stations.txt updated with %s stations' % slength)


if __name__ == "__main__":
    main(sys.argv[1:])
