#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import datetime
import os
import getopt
import requests as r
import re
import html

URL = 'http://mobil.ul.nu/stadsbuss/vemos2_web.dll/betatest/mhpl?hplnr=%s&starttid=%s'
stationsFile = 'stations.txt'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:26.0) Gecko/20100101 Firefox/26.0'
}


def print_usage():
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
    print("       --station stationName (-s short option)")
    print("             Gets the current timetable for stationName provided.")
    print("             Multiple stations can be entered, dividing using |")
    print("")
    print("             Optional: ")
    print("")
    print("             --time HHMM (-t short option) ")
    print("                    Gets the current timetable for the specified time.")
    print("")
    print("       --fetch (-f short option)")
    print("             Fetches all UL stations with ID between 700001 and 700611 and")
    print("             adds them to %s. This file is used when getting a timetable without" % stationsFile)
    print("             hammering their server.")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "s:t:hfl", ["station=", "time=", "help", "fetch"])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    opt = None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
        elif opt in ("-s", "--station"):
            time = None
            for sopt, argt in opts:
                if sopt in ("-t", "--time"):
                    time = argt
                    break
            parse_stations(arg, time)
        elif opt in ("-f", "--fetch"):
            fetch_stations()
        elif opt in ("-l", "--list"):
            list_stations()
    if not opt:
        print_usage()


def list_stations():
    with open(stationsFile, 'r') as stations:
        print(stations.read())


def parse_stations(stationname, time=False):
    for station_name in stationname.split('|'):
        with open(stationsFile, 'r') as stations:
            for station in re.finditer('.*' + station_name + '.*', stations.read(), flags=re.IGNORECASE):
                station = station.group(0)
                stationname = station.split(',')[-1]
                stationid = station.split(',')[0]

                get_station(stationname, stationid, time)


def get_station(stationname, stationid, time=False):
    if not time:
        time = datetime.datetime.now().time().strftime("%H:%M")

    url = URL % (stationid, time)
    response = r.get(url, headers=headers)
    remove = [
        '</b>',
        '\r'
    ]
    destinations = {}
    departures = {}
    print("Avgångar från %s" % stationname)
    print("")
    destcount = 0
    depcount = 0
    for dst in re.finditer('[0-9].* mot.*', response.text, re.MULTILINE):
        dst = str(html.unescape(dst.group(0))).ljust(35)
        for val in remove:
            dst = re.sub(val, '', dst, flags=re.MULTILINE)
        destination = {
            destcount: dst
        }
        destinations.update(destination)
        destcount += 1

    for departure in re.finditer('.*\([0-9]{2}:[0-9]{2}\)', response.text, re.VERBOSE):
        departure = departure.group(0)
        departure = re.sub('.*om', ' om', departure)
        departure = {
            depcount: departure
        }
        departures.update(departure)
        depcount += 1

    if destinations:
        for key in destinations:
            print(destinations[key] + departures[key])
    else:
        print("Inga avgångar från %s klockan %s idag" % (stationname, time))

    print('')


# noinspection PyUnreachableCode
def fetch_stations():
    print('Dont use this for now, use the provided %s' % stationsFile)
    sys.exit(0)
    remove = [
        "Avgångar från ",
        " i Uppsala.*"
    ]
    if os.path.isfile(stationsFile):
        os.remove(stationsFile)
    for knownstations in range(700001, 700612):
        knownstations = str(knownstations)

        with open('data/' + knownstations + '.html', 'r') as infile:
            for match in re.finditer('Avg.* <', infile.read(), flags=re.MULTILINE):
                station = str(match.group(0))

                for val in remove:
                    station = re.sub(val, '', station, flags=re.MULTILINE)

                if len(station) > 0:
                    with open(stationsFile, "a") as myfile:
                            myfile.write(knownstations + ',' + station + '\n')
    with open(stationsFile, 'r') as f:
        slength = len(f.readlines())
    print('stations.txt updated with %s stations' % slength)


if __name__ == "__main__":
    main(sys.argv[1:])
