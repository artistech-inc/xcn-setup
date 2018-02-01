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

trap ctrl_c INT

ctrl_c() {
  kill $(jobs -p)
  exit 1
}

avg() {
  if [ $2 -eq 0 ]; then
    echo "0.000"
    return
  fi

  python -c "print '%.3f' % ($1.0 / $2)"
}

parse_outdir() {
  OUTDIR=$1
  
  if [ ! -d "$OUTDIR" ]; then
    echo "usage(): $0 <output directory>"
    exit 1
  fi

  cd $OUTDIR
  echo $OUTDIR
  NODES_CFG=`pwd`/*.config
  rm -f NODE_PCAP_STATS TOTAL_PCAP_STATS TOTAL_EMANE_STATS
  
  # 84 n84 172.16.1.85/24 10.0.0.85/24
  while read line; do
    node=`echo $line |awk '{print $2}'`
    ip=
    for i in `grep $node $NODES_CFG |awk '{for (i=4;i<=NF;i++) print $i}'`; do
      if [ $i != "0.0.0.0" ]; then
        ip="$ip -i `echo $i | awk -F '/' '{print $1}'`"
      fi
    done

    if [ -f ${node}.pcap ]; then
      ${GRAPHING_LIB}/parse_tcpdump.py ${ip} -q ${node}.pcap port 18735 > ${node}.pcap.stats
    fi

    if [ -f ${node}.pcap.stats ]; then
      cat ${node}.pcap.stats >> NODE_PCAP_STATS
    fi
  done < $NODES_CFG

  egrep -q -m 1 'UDP|TCP' NODE_PCAP_STATS
  if [ $? -eq 0 ]; then
    # parse total tcpdump output
    ${GRAPHING_LIB}/parse_totals.py -q NODE_PCAP_STATS > TOTAL_PCAP_STATS
  else
    # if we don't have any data in the NODE_PCAP_STATS file, delete it
    rm NODE_PCAP_STATS
  fi

  # if a parse_test_results function was defined, call it. 
  type parse_test_results &> /dev/null
  if [ $? -eq 0 ]; then
    parse_test_results
  fi

  # parse emane stats
  $XCN_SCRIPT_LIB/parse-emane-stats.py . > TOTAL_EMANE_STATS
  [ ! -s TOTAL_EMANE_STATS ] && rm TOTAL_EMANE_STATS

  echo $1
  cat $1/VARS 

  cd $CUR_DIR
}

run_bandwidth_loop() {
  BANDWIDTHS=`grep BANDWIDTH */VARS|awk -F '=' '{print $2}' |sort -n -u`

  for BANDWIDTH in $BANDWIDTHS; do
    type init_bandwidth_loop &> /dev/null
    if [ $? -eq 0 ]; then
      init_bandwidth_loop
    fi

    total_shim_files=
    total_pcap_files=
    total_emane_files=

    pcap_n=0
    emane_n=0
    shim_n=0

    DIRS=`for i in 20*; do [ ! -d "$i" ] && continue; grep -q -w "BANDWIDTH=${BANDWIDTH}" $i/VARS && echo $i; done`
    for d in $DIRS; do
      # The caller can create a function to filter out certain directories when
      # parsing
      type filter_bandwidth_dirs &> /dev/null
      if [ $? -eq 0 ]; then
        filter_bandwidth_dirs || continue
      fi

      if [ -f $d/TOTAL_SHIM_STATS ]; then
        total_shim_files="$total_shim_files $d/TOTAL_SHIM_STATS"
        shim_n=$(expr $shim_n + 1)
      fi

      if [ -f $d/TOTAL_PCAP_STATS ]; then
        total_pcap_files="$total_pcap_files $d/TOTAL_PCAP_STATS"
        pcap_n=$(expr $pcap_n + 1)
      fi

      if [ -f $d/TOTAL_EMANE_STATS ]; then
        total_emane_files="$total_emane_files $d/TOTAL_EMANE_STATS"
        emane_n=$(expr $emane_n + 1)
      fi
    done

    type parse_bandwidth_dirs &> /dev/null
    if [ $? -eq 0 ]; then
      parse_bandwidth_dirs
    fi

    # parse shim output for this bandwidth
    if [ ! -z "$total_shim_files" ]; then
      shim_log=`echo ${total_shim_files} |awk '{print $1}'`

      if [ ! -f "${output_prefix}shim.csv" ]; then
        echo -n "Bandwidth	" > ${output_prefix}shim.csv
        while read line ; do 
          entry=`echo $line |awk -F ':' '{print $1}'`
          if [ ! -z "$entry" ]; then
            echo -n "$entry	" >> ${output_prefix}shim.csv
          fi
        done < $shim_log
        echo >> ${output_prefix}shim.csv
      fi

      echo -n "$BANDWIDTH	" >> ${output_prefix}shim.csv
      while read line ; do 
        entry=`echo $line |awk -F ':' '{print $1}'`
        if [ ! -z "$entry" ]; then
          item=`grep "$entry" ${total_shim_files} |awk '{sum+=$NF};END {print sum}'`
          echo -n "$(avg $item $shim_n)	" >> ${output_prefix}shim.csv
        fi
      done < $shim_log
      echo >> ${output_prefix}shim.csv
    fi

    # Parse TOTAL_PCAP_STATS files
    if [ $pcap_n -gt 0 ]; then
      if [ ! -f "${output_prefix}pcap.csv" ]; then
        echo 'Bandwidth	Bytes Sent	Bytes Received	Packets Sent	Packets Received	Packets Dropped' > ${output_prefix}pcap.csv
      fi
      bsent=`grep -A 1 'Bytes Sent' ${total_pcap_files} |grep -o "total: [0-9]*" |awk '{sum+=$2};END {print sum}'`
      brcvd=`grep -A 1 'Bytes Received' ${total_pcap_files} |grep -o "total: [0-9]*" |awk '{sum+=$2};END {print sum}'`
      psent=`grep -A 1 'Packets Sent' ${total_pcap_files} |grep -o "total: [0-9]*" |awk '{sum+=$2};END {print sum}'`
      prcvd=`grep -A 1 'Packets Received' ${total_pcap_files} |grep -o "total: [0-9]*" |awk '{sum+=$2};END {print sum}'`
      pdrop=`expr $psent - $prcvd`

      echo "$BANDWIDTH	$(avg $bsent $pcap_n)	$(avg $brcvd $pcap_n)	$(avg $psent $pcap_n)	$(avg $prcvd $pcap_n)	$(avg $pdrop $pcap_n)" >> ${output_prefix}pcap.csv
    fi

    # Parse TOTAL_EMANE_STATS files
    if [ $emane_n -gt 0 ]; then
      if [ ! -f "${output_prefix}emane.csv" ]; then
        echo 'Bandwidth	Bytes Sent	Bytes Received	Packets Sent	Packets Received	Packets Dropped' > ${output_prefix}emane.csv
      fi
      bsent=`grep -m 1 'Num Bytes Tx:' ${total_emane_files} |grep -o 'Tx:.*[0-9][0-9]*' |awk '{sum+=$2};END {print sum}'`
      brcvd=`grep -m 1 'Num Bytes Rx:' ${total_emane_files} |grep -o 'Rx:.*[0-9][0-9]*' |awk '{sum+=$2};END {print sum}'`
      psent=`grep -m 1 'Num Pkts Tx:' ${total_emane_files} |grep -o 'Tx:.*[0-9][0-9]*' |awk '{sum+=$2};END {print sum}'`
      prcvd=`grep -m 1 'Num Pkts Rx:' ${total_emane_files} |grep -o 'Rx:.*[0-9][0-9]*' |awk '{sum+=$2};END {print sum}'`
      pdrop=`grep -m 1 'Total Drops:' ${total_emane_files} |grep -o 'Drops:.*[0-9][0-9]*' |awk '{sum+=$2};END {print sum}'`

      echo "$BANDWIDTH	$(avg $bsent $emane_n)	$(avg $brcvd $emane_n)	$(avg $psent $emane_n)	$(avg $prcvd $emane_n)	$(avg $pdrop $emane_n)" >> ${output_prefix}emane.csv
    fi
  done
}

if [ ! -f "$SCENARIO_FILE" ]; then
  echo "Environment variable 'SCENARIO_FILE' must be defined and point to a .scn file"
  exit 1
fi

CUR_DIR=`pwd`
GRAPHING_LIB=$(cd ../graphing && pwd)
XCN_SCRIPT_LIB=$(cd ../xcn/scripts && pwd)

OUTPUT_DIR=$(eval echo `grep OUTPUT_DIR $SCENARIO_FILE |awk -F '=' '{print $2}' |sed -e 's/\"//g'`)
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "Unable to find or detect output directory: $OUTPUT_DIR"
  exit 1
fi

cd $OUTPUT_DIR

CSV_ONLY=0
PARSE_ONLY=0
while getopts ":cp" opt; do
  case $opt in
    c)
      CSV_ONLY=1
      ;;
    p)  #set option "b"
      PARSE_ONLY=1
      ;;
    \?)
      echo "usage: $0 [-p|-c] <directories>"
      ;;
  esac
done

shift $((OPTIND-1))  #This tells getopts to move on to the next argument.

# Run individual run parsers
if [ $CSV_ONLY -eq 0 ]; then
  if [ -d "$1" ]; then
    DIRS=$*
  else
    DIRS=$OUTPUT_DIR/20*
  fi

  n=0
  for i in $DIRS; do
    [ ! -d "$i" ] && continue
    parse_outdir $i &
    n=$(expr $n + 1)
    while [ `jobs -p |wc -l` -gt 9 ]; do
      sleep 1
    done
  done
fi
wait

# if we were given a -p argument, exit after we finish parsing
if [ $PARSE_ONLY -eq 1 ]; then 
  exit 0
fi

rm *shim.csv *pcap.csv *emane.csv
