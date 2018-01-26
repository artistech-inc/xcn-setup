#! /bin/bash
#
# Copyright (c) 2011-2016 Raytheon BBN Technologies Corp.  All rights reserved.
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
# $Id$

#if [ $EUID -eq 0 ]; then
#  echo "This script must not be run as root"
#  exit 1
#fi

KILLSCRIPT=$(cd `dirname $0` && pwd)/$0

COLLECT_OUTPUT=0
IS_REMOTE=0
RUNID=
OUTDIR=/home/${USER}/sim_runs
TAG=$(date +"%Y%m%d-%H%M%S-$RANDOM")

re='^[0-9]+$'
while [ $# -gt 0 ]; do
  if [ "$1" = "-c" ]; then
    COLLECT_OUTPUT=1

  elif [ "$1" = "-r" ]; then
    IS_REMOTE=1
    TAG=$2
    shift

  elif [[ $1 =~ $re ]] ; then
    RUNID="$1"

  else
    OUTDIR=$1

  fi
  shift
done

kill_name() {
  pids=`ps -ef |egrep "$*" |grep -v "grep" |awk '{print $2}'`
  if [ ! -z "$pids" ]; then
    sudo kill $pids
  fi
}

kill_lxcs() {
  ps -ef |grep lxc-execute |grep -o -- "-n [^ ][^ ]*.$1" |sed -e 's/-n //' | \
    while read i; do sudo lxc-stop -n $i ; done 
}

kill_dockers() {
  for n in `docker container ls |grep -- "n[0-9]*-$1" |awk '{print $1}'`; do
    docker container kill $n
    docker container rm $n
  done
  docker network rm xcn.$1
}

del_route() {
  [ -z "$1" ] && continue
  for i in `route -n |grep ^10.$1 |awk '{print $1}'`; do
    sudo ip route del $i/24
  done
}

del_iface() {
  IFACE=`ifconfig |grep -o "^e[thm]*[0-9][0-9]*.${1}" |uniq`
  [ -z "$IFACE" ] && return
  sudo ifconfig $IFACE down
  sudo ip link del $IFACE
}

del_bridge() {
  BRIDGE=`brctl show |awk '{print $1}' |grep -m 1 "lxcbr.${1}"`
  [ -z "$BRIDGE" ] && return

  sudo ip link set $BRIDGE down
  sudo brctl delbr $BRIDGE

  while (ip link show | grep -q $BRIDGE); do
    sleep 1
  done
}

do_move() {
  [ $COLLECT_OUTPUT -eq 0 -o ! -d "$1" ] && return

  d=$OUTDIR/$(basename $1)-$TAG

  mkdir -p $OUTDIR
  if [ $? -ne 0 ]; then
    echo "Unable to make directory $OUTDIR"
    exit 1
  fi

  mv -i "$1" $d
  sudo chown -R ${USER}:${USER} $OUTDIR

  if [ ${IS_REMOTE} -eq 0 -a -f $d/MACHINE_LIST ]; then
    for remote in `grep "REMOTE" $d/MACHINE_LIST |awk '{print $2}'`; do
      scp -r $remote:$d/* $d/
    done
  fi

  echo "Output saved to $d"
}

del_all() {
  [ -z "$1" ] && return

  # RUN ID of 0 is illegal
  [ "$1" = "0" ] && return
  RUNID=$1
  DIR=/tmp/xcn.$RUNID

  if [ ${IS_REMOTE} -eq 0 -a -f $DIR/MACHINE_LIST ]; then
    FLAGS="-r $TAG $1 $OUTDIR"
    [ $COLLECT_OUTPUT -eq 1 ] && FLAGS="-c $FLAGS"

    for remote in `grep "REMOTE" $DIR/MACHINE_LIST |awk '{print $2}'`; do
      ssh -t $remote "bash $KILLSCRIPT $FLAGS"
    done
  fi

  kill_lxcs $RUNID
  kill_dockers $RUNID
  del_route $RUNID
  del_iface $RUNID
  #del_bridge $RUNID
  kill_name "emaneeventservice.$RUNID\.log"
  kill_name "zmq_mcast_tunnel"

  if [ -d "$DIR" ]; then
    do_move $DIR
    rm -rf $DIR
  fi
}

if [ ! -z "$RUNID" ]; then
  del_all $RUNID

else
  for dir in /tmp/xcn.*; do 
    [ $dir = '/tmp/xcn.*' ] && break
    
    RUNID="`echo $dir |awk -F '.' '{print $2}'`"
    del_all $RUNID
  done

  for i in `ifconfig |egrep -o '(xcn|em1|eth0|lxcbr|veth[0-9][0-9]*\.[0-9][0-9]*)\.[0-9][0-9]*' |awk -F '.' '{print $2}' |sort -u`; do
    del_all $i
  done

  for i in `route -n |grep -o '^10.[0-9][0-9]*.[0-9][0-9]*.0' |awk -F '.' '{print $2}'`; do
    del_all $i
  done
fi
