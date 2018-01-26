#!/bin/bash

./install_cnr_bridge.sh

NODE_COUNT=`wc -l cnr.eel | awk '{print $1}'`
Nodes=()
for (( i=1; i<=$NODE_COUNT; i++))
do
    echo "./emane_client.sh n$i"
    ./emane_client.sh n$i &
    sleep 1
done
