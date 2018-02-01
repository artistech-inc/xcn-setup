#!/bin/bash

./install_cnr_bridge.sh

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
    CNR_ARGS=$CNR_ARGS" -xcn "$i
done

./run_emane_clients.sh
sleep 1

BRIDGE_JAR=`pwd`/Vbs3EmanePlugin/target/cnr-bridge-1.0.jar

IP=`hostname -I | awk '{print $1}'`
echo ""
echo "Bridge Server IP: "$IP
echo ""

echo "java -cp $BRIDGE_JAR com.artistech.cnr.BridgeServer $CNR_ARGS -log FINER"
java -cp $BRIDGE_JAR com.artistech.cnr.BridgeServer $CNR_ARGS -log FINER
