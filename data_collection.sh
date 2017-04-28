#!/bin/bash

connect_vehicle()
{
	k=0
	echo "Connecting vehicle $1 at loc $k"
	python3 solution_vehicle_client.py --loc $k
	k+=1
}
# Range of solution vehicles to test against
for ((i = 1; i <= 1; i++))
do
# Output file name containing sv number
filename='data_sv'
fileext='.csv'
filename+=$i
filename+=$fileext
echo "Starting traffic model with $i sv"
# Run the traffic model
python3 traffic_model_data_collection.py --run 1000 --sv $i --fn $filename &
# Give it time to initiate before connecting a sv
sleep 0.2
connect_vehicle 1
# When the first run is complete, reconnect all the sv based on reading from stdin
# This stupid shit doesn't work at the moment
while read line
do
	echo "line is $line"
	if [ $line == "Run complete" ]
	then
		for (( j = 1; j <= i; j++))
		do
			connect_vehicle
		done
	fi
done < "${1:-/dev/stdin}"
done

