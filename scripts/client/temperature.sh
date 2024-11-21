#!/bin/bash

printf "%-20s%5s\n" "TIMESTAMP" "TEMP"
printf "%25s\n" "-------------------------"

while true
do
	temp=$(vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*')
	timestamp=$(date '+%d/%m/%Y %H:%M:%S');
	printf "%-20s%5s\n" "$timestamp" "$temp"
	sleep 10
done