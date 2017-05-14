#!/bin/bash
rm points.csv
for i in ./*.gpx.csv
do
  skip=true
  # Get the flight id
  IFS='.' read -a flight <<< "$i"
  flight_id=${flight[1]}
  flight_id=${flight_id:1:${#flight_id}}
  echo ${flight_id}
  # Parse each line and prepend the flight id.
  while IFS=, read point lat lon alt date time
  do
   if [ "$skip" = true ]; then
    skip=false
   else
    echo "${flight_id},${lat},${lon},${time}" >>points.csv
   fi
  done <${i}
done
