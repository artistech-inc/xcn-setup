#!/bin/bash

NODE_COUNT=`wc -l cnr.eel | awk '{print $1}'`
Nodes=()
for (( i=1; i<=$NODE_COUNT; i++))
do
    node=`./run_cmd.sh n$i ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}'`
    echo $node
    Nodes[$i - 1]=$node
done
CNR_ARGS=

for i in "${Nodes[@]}"
do
    CNR_ARGS=$CNR_ARGS" -client "$i
done

IP=`hostname -I | awk '{print $1}'`

BRIDGE_JAR=`pwd`/Vbs3EmanePlugin/target/cnr-bridge-1.0.jar

echo "./run_cmd.sh $1 java -jar $BRIDGE_JAR -cast uni $CNR_ARGS -server $IP -log INFO"
./run_cmd.sh $1 java -jar $BRIDGE_JAR -cast uni $CNR_ARGS -server $IP -log INFO 

