#!/bin/bash

# Generates a list of flights to download.

while read flights
do
    IFS=',' read -ra FLIGHT <<< "$flights"
    echo ${FLIGHT[5]}
done <../OLC/flight/flights.csv