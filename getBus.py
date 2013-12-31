#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
import datetime
import os
import getopt
import requests as r
import re
import HTMLParser


URL = 'http://mobil.ul.nu/stadsbuss/vemos2_web.dll/betatest/mhpl?hplnr=%s&starttid=%s'
stationsFile = 'stations.txt'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:26.0) Gecko/20100101 Firefox/26.0'
}


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
    print("             Multiple stations can be inputed by dividing with |")
    print("")
    print("       --fetch (-f short option)")
    print("             Fetches all UL stations with ID between 700001 and 700611 and")
    print("             adds them to %s. This file is used when getting a timetable without" % stationsFile)
    print("             hammering their server.")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "g:t:hfl", ["get","time","help", "fetch"])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    opt = None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printUsage()
        elif opt in ("-g", "--get"):
            time = None
            for opt, argt in opts: 
                if opt in ("-t", "--time"):
                    time = argt
                    break
            parseStations(arg,time)
        elif opt in ("-f", "--fetch"):
            fetchStations()
        elif opt in ("-l", "--list"):
            listStations()
    if not opt:
        printUsage()


def listStations():
    with open(stationsFile, 'r') as stations:
        print stations.read()

def parseStations(stationName, time=False):
    for station in stationName.split('|'):
        with open(stationsFile, 'r') as stations:
            for station in re.finditer('.*' + station + '.*', stations.read(), flags=re.MULTILINE):
                station = station.group(0).decode('utf8')
                stationName = station.split(',')[-1]
                stationId = station.split(',')[0]

                getStation(stationName, stationId, time)


def getStation(stationName, stationId, time=False):
    if not time:
        time = datetime.datetime.now().time().strftime("%H:%M")

    pars = HTMLParser.HTMLParser()
    url = URL % (stationId, time)
    response = r.get(url, headers=headers)
    remove = [
        '</b>',
        '\r'
    ]
    destinations = {}
    departures = {}
    print("Departures from %s" % stationName)
    print("")
    destcount = 0
    depcount = 0
    for dst in re.finditer('[0-9].* mot.*', response.text, re.MULTILINE):
        dst = unicode(pars.unescape(dst.group(0).encode('utf8'))).ljust(35)
        for val in remove:
            dst = re.sub(val, '', dst, flags=re.MULTILINE)
        destination = {
            destcount: dst
        }
        destinations.update(destination)
        destcount = destcount + 1

    for departure in re.finditer('.*\([0-9]{2}:[0-9]{2}\)', response.text, re.VERBOSE):
        departure = unicode(pars.unescape(departure.group(0).encode('utf8')))
        departure = re.sub('.*om', ' om', departure)
        departure = {
            depcount: departure
        }
        departures.update(departure)
        depcount = depcount + 1

    for key in destinations:
        print(destinations[key] + departures[key])

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
