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

dir=`ls -d /tmp/xcn.[0-9]*`
numdirs=`echo $dir | wc -w `
if [ $numdirs -ne 1 ]; then
  echo "ERROR: Found $numdirs running XCN instances. This script only works with 1"
  exit 1
fi

runid=`echo $dir |awk -F '.' '{print $2}'`
numnodes=`ls -d ${dir}/n[0-9]*-[0-9]* |wc -w`
info=`grep eventservicegroup ${dir}/emane_configs/eventservice.xml |grep -o '[0-9]*.[0-9]*.[0-9]*.[0-9]*:[0-9]*'`
mcaddr=`echo $info |awk -F ':' '{print $1}'`

eventport=`echo $info |awk -F ':' '{print $2}'`
controlport=`grep controlportendpoint $dir/emane_configs/platform1.xml | grep -o ":[0-9]*" |sed -e 's/://'`

if [ $# -eq 1 ]; then
  #emaneevent-tdmaschedule -i lxcbr.${runid} -g ${mcaddr} -p ${eventport} $1
  emaneevent-tdmaschedule -i xcn.${runid} -g ${mcaddr} -p ${eventport} $1

else
  echo "ERROR: Must specify a TDMA XML file"
fi
