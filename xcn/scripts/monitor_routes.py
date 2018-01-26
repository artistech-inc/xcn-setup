#! /usr/bin/env python
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

import sys
import os
import re
import time

ipToNode = {}

entry_filter = re.compile("^(\d+.\d+.\d+.[1-9]\d*)\s+(\d+.\d+.\d+.\d+).*")
if len(sys.argv) > 1:
  # 0	n0	172.16.1.1/24	10.0.0.1/24
  f = open(sys.argv[1], 'r')
  for line in f.readlines():
    s = line.split()
    nodeName = s[1]
    for ip in s[2:]:
      if ip != "0.0.0.0":
        ipToNode[ip.split('/')[0]] = nodeName

else:
  filter = False

#route -n |grep ^1
#10.0.3.0        0.0.0.0         255.255.255.0   U     0      0        0 lxcbr0
#192.1.120.0     0.0.0.0         255.255.255.0   U     0      0        0 eth0
#192.168.122.0   0.0.0.0         255.255.255.0   U     0      0        0 virbr0

nexthops = {}
curtime = 0.0

while True:
  doflush = False

  for line in os.popen("route -n").readlines():
    match = entry_filter.match(line)
    if match:
      dest = match.group(1)
      nhop = match.group(2)

      if ipToNode.has_key(dest):
        dest = ipToNode[dest]

      if nhop == "0.0.0.0" and not nexthops.has_key(dest):
        print "%.2f add nexthop %s" % (curtime, dest)
        doflush = True
        nexthops[dest] = nhop
      elif nhop != "0.0.0.0" and nexthops.has_key(dest):
        print "%.2f remove nexthop %s" % (curtime, dest)
        doflush = True
        nexthops.pop(dest)

  try:
    if doflush:
      sys.stdout.flush()
    time.sleep(1)
  except:
    sys.exit(0)

  curtime += 1.0
