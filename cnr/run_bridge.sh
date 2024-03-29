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

index=0
for var in "$@"
do
    CNR_ARGS=$CNR_ARGS" -pair "${Nodes[$index]}:$var
    index=$((index+1))
done

BRIDGE_JAR=`pwd`/Vbs3EmanePlugin/target/cnr-bridge-1.0.jar

echo "java -cp $BRIDGE_JAR com.artistech.cnr.BridgeServer $CNR_ARGS -log FINER"
java -cp $BRIDGE_JAR com.artistech.cnr.BridgeServer $CNR_ARGS -log FINER
