#!/bin/bash

# Example: /home/ubuntu/git/flightbit/downloader/rap.sh -i /home/ubuntu/git/flightbit/downloader/thermals.csv -o /home/ubuntu/RAP

echo "Starting RAP Download Job."

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
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done
echo INPUT  = "${INPUT}"
echo OUTPUT     = "${OUTPUT}"

i=1
while IFS=, read flight_id longitude latitude heigth vario alt_diff thermal_time
do
    test $i -eq 1 && ((i=i+1)) && continue
    IFS=' ' read -a time_stamp <<< "$thermal_time"
    thermal_day=${time_stamp[0]}
    thermal_hour=${time_stamp[1]}
    IFS='-' read -a day_stamp <<< "$thermal_day"
    IFS=':' read -a hour_stamp <<< "$thermal_hour"
    year=${day_stamp[0]}
    month=${day_stamp[1]}
    day=${day_stamp[2]}
    hour=${hour_stamp[0]}

    model="rap_130"
    format="grb2"
    todate=$(date -d ${year}-${month}-${day} +%s)
    cond=$(date -d 2012-05-01 +%s)
    cond_2=$(date -d 2008-12-31 +%s)
    if [ $todate -le $cond ]; then
        model="ruc2anl_130"
    fi
    if [ $todate -le $cond_2 ]; then
        model="ruc2_252"
        format="grb"
    fi

    grib_file="${model}_${year}${month}${day}_${hour}00_001.${format}"
    grib_url="https://nomads.ncdc.noaa.gov/data/rucanl/${year}${month}/${year}${month}${day}/${grib_file}"

    echo "GRIB URL: ${grib_url}"

    if [ -e "${OUTPUT}/GRIB/${grib_file}" ]
    then
        echo "Skipping ${grib_file}"
    else
        echo "Downloading ${grib_file}"
        curl -b /tmp/cookies.tmp -o ${OUTPUT}/GRIB/${grib_file} ${grib_url}
        if [ -e "${OUTPUT}/GRIB/${grib_file}" ]
        then
            echo "Downloaded ${OUTPUT}/GRIB/${grib_file}"
        else
            echo "Failed to download ${grib_file}. Exiting now..."
            exit
        fi
    fi
done <${INPUT}