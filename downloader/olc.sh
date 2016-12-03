#!/bin/bash

# Example: /home/ubuntu/git/flightbit/downloader/olc.sh -i /home/ubuntu/git/flightbit/downloader/flights.csv -o /home/ubuntu/OLC/IGC -u flightbit -p <OLC password>

echo "Starting OLC Download Job."

# Parsing arguments from the command line.
while [[ $# > 1 ]]
do
key="$1"

case $key in
    -i|--input)
    INPUT="$2"
    shift # past argument
    ;;
    -o|--output)
    OUTPUT="$2"
    shift # past argument
    ;;
    -u|--user)
    USER="$2"
    shift # past argument
    ;;
    -p|--password)
    PASSWORD="$2"
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done
echo INPUT  = "${INPUT}"
echo OUTPUT     = "${OUTPUT}"
echo USER    = "${USER}"

# Start an HTTP session
curl -c /tmp/cookies.tmp http://www.onlinecontest.org/olc-2.0/gliding/index.html

# Login
curl -b /tmp/cookies.tmp -X POST https://www.onlinecontest.org/olc-2.0/secure/login.html -d "_ident_=${USER}&_name__=${PASSWORD}&ok_par.x=16&ok_par.y=8"

# Start downloading
#curl -b /tmp/cookies.tmp -o 198290884.igc http://www.onlinecontest.org/olc-2.0/gliding/download.html?flightId=198290884

while read flight
do
    if [ -e "${OUTPUT}/$flight.igc" ]
    then
        echo "Skipping $flight"
    else
        echo "Downloading $flight"
        curl -b /tmp/cookies.tmp -o ${OUTPUT}/$flight.igc http://www.onlinecontest.org/olc-2.0/gliding/download.html?flightId=${flight}
        if [ -e "${OUTPUT}/$flight.igc" ]
        then
            echo "Downloaded ${OUTPUT}/$flight.igc"
        else
            echo "Failed to download flight $flight. Exiting now..."
            exit
        fi
    fi
done <${INPUT}