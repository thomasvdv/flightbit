#!/usr/bin/env bash

echo "Loading IGC files to database."

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

for igc in ${INPUT}/*.igc
do
    echo $igc
done