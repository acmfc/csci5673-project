#!/usr/bin/env bash

SV_NUM=$1
RUN=$2
OUTPUT_FILE=$3

echo $SV_NUM

python3 traffic_model.py --sv $SV_NUM --run $RUN >> $OUTPUT_FILE &

i=0
while [ $i -lt $SV_NUM ]; do
    python3 solution_vehicle_client.py &

    i=$[$i+1]
done