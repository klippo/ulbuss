Requirements:
    requests 1.2.3+ (pip install requests)


Usage: ./getBus.py [ options ]

Options:
         -[lgfh] [ --list ] [ --help ]
                      [ --get stationName ]
                      [ --fetch ]

       --list (-l short option)
             Lists all fetched stations.

       --help (-h short option)
             Shows this screen.

       --station stationName (-s short option)
             Gets the current timetable for stationName provided.
             Multiple stations can be entered, dividing using |

             Optional: 

             --time HHMM (-t short option) 
                    Gets the current timetable for the specified time.

       --fetch (-f short option)
             Fetches all UL stations with ID between 700001 and 700611 and
             adds them to stations.txt. This file is used when getting a timetable without
             hammering their server.
