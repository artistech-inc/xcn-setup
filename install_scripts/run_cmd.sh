#!/usr/bin/env bash
#
# Copyright (c) 2011-2018 Raytheon BBN Technologies Corp.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of Raytheon BBN Technologies nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# @author Will Dron <will.dron@raytheon.com>

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
