#!/bin/bash

#RUNID=`ifconfig |grep -o 'lxcbr\.[0-9]*' |awk -F '.' '{print $2}'`
RUNID=`docker network ls |grep xcn |awk '{print $2}' |awk -F '.' '{print $2}'`
if [ `echo $RUNID |wc -w` -eq 0 ]; then
  echo "No XCN instances are running"
  exit 1

elif [ `echo $RUNID |wc -w` -gt 1 ]; then
  echo "Unable to run command, multiple XCN instances are running: $RUNID"
  exit 1
fi

NODEFILE="/tmp/xcn.${RUNID}/emane_configs/NODES"
if [ ! -f "$NODEFILE" ]; then
  echo "Unable to find file $NODEFILE, exiting"
  exit 1
fi

NODE=$1
shift
if [ -z "$NODE" ]; then
  echo "usage(): $0 <node> <command>"
  exit 1
fi

# This loop will replace any instance of IP.a with the first ipaddress
# associated with Node 'a' (i.e. IP.3). It will also replace IP.a.b with the
# ipaddress of Node 'a' subnet 'b' (i.e. IP.3.1).
new_cmd=""
for word in $*; do
  if [[ ${word} =~ ^IP.[0-9]+$ ]]; then
    nodeid=${word##*.}
    word=$(grep -m 1 "node:$nodeid " ${NODEFILE} |awk '{print $4}')
    if [ -z "$word" ]; then
      echo "Unable to find node ID $nodeid"
      exit 1
    fi
  elif [[ ${word} =~ ^IP.[0-9]+.[0-9]+$ ]]; then
    nodeid=$(echo ${word} | awk -F '.' '{print $2}')
    subnetid=${word##*.}
    word=$(grep -m 1 "node:$nodeid .* subnet:$subnetid " ${NODEFILE} |awk '{print $4}')
    if [ -z "$word" ]; then
      echo "Unable to find node ID $nodeid"
      exit 1
    fi
  fi

  new_cmd="$new_cmd $word"
done

#sudo lxc-attach -n $NODE-$RUNID -- $new_cmd
if [ -z "$new_cmd" ]; then
  echo "=========================================="
  echo "Attaching to docker container $NODE-$RUNID"
  echo "To detach, use ctrl-p ctrl-q"
  echo "=========================================="
  docker attach $NODE-$RUNID

else
  docker exec $NODE-$RUNID $new_cmd
fi
