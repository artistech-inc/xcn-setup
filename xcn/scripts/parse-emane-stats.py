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

# nem 1   mac BroadcastPacketAcceptTable0
# | NEM | Num Pkts Tx | Num Bytes Tx | Num Pkts Rx | Num Bytes Rx |
# | 1   | 8           | 696          | 0           | 0            |
# | 3   | 0           | 0            | 5           | 390          |
# | 4   | 0           | 0            | 2           | 140          |
# | 5   | 0           | 0            | 2           | 140          |
# | 6   | 0           | 0            | 2           | 140          |
# | 7   | 0           | 0            | 2           | 140          |
# | 8   | 0           | 0            | 2           | 140          |
# | 10  | 0           | 0            | 2           | 160          |
# 
# nem 1   mac BroadcastPacketDropTable0
# | NEM | SINR | Reg Id | Dst MAC | Queue Overflow | Bad Control | Bad Spectrum Query | Flow Control |
# | 9   | 3    | 0      | 0       | 0              | 0           | 0                  | 0            |
# | 10  | 3    | 0      | 0       | 0              | 0           | 0                  | 0            |
# | 11  | 2    | 0      | 0       | 0              | 0           | 0                  | 0            |
# | 24  | 2    | 0      | 0       | 0              | 0           | 0                  | 0            |
# 
# nem 1   mac NeighborMetricTable
# | NEM   | Rx Pkts | Tx Pkts | Missed Pkts | BW Util | Last Rx       | Last Tx       | SINR Avg      | SINR Stdv | NF Avg | NF Stdv | Rx Rate Avg | Tx Rate Avg |
# | 3     | 5       | 0       | 0           | 19498   | 1430480148.85 | 0.0           | 20.8505077362 | 0.0       | -110.0 | 0.0     | 160000      | 0.0         |
# | 4     | 2       | 0       | 0           | 7000    | 1430480146.91 | 0.0           | 20.8505077362 | 0.0       | -110.0 | 0.0     | 160000      | 0.0         |
# | 5     | 2       | 0       | 0           | 7000    | 1430480147.27 | 0.0           | 20.8505077362 | 0.0       | -110.0 | 0.0     | 160000      | 0.0         |
# | 6     | 2       | 0       | 0           | 7000    | 1430480148.57 | 0.0           | 20.8505077362 | 0.0       | -110.0 | 0.0     | 160000      | 0.0         |
# | 7     | 2       | 0       | 0           | 7000    | 1430480148.12 | 0.0           | 14.8294429779 | 0.0       | -110.0 | 0.0     | 160000      | 0.0         |
# | 8     | 2       | 0       | 0           | 7000    | 1430480149.36 | 0.0           | 6.87036418915 | 0.0       | -110.0 | 0.0     | 160000      | 0.0         |
# | 10    | 2       | 0       | 1           | 7999    | 1430480149.9  | 0.0           | 6.87036418915 | 0.0       | -110.0 | 0.0     | 160000      | 0.0         |
# | 65535 | 0       | 8       | 0           | 0       | 0.0           | 1430480147.73 | 0.0           | 0.0       | 0.0    | 0.0     | 0.0         | 160000      |
# 
# nem 1   mac NeighborStatusTable
# | NEM   | Rx Pkts | Tx Pkts | Missed Pkts | BW Util Ratio | SINR Avg | NF Avg | Rx Age        |
# | 3     | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 678.630310059 |
# | 4     | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 680.574279785 |
# | 5     | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 680.214294434 |
# | 6     | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 678.918334961 |
# | 7     | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 679.366333008 |
# | 8     | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 678.126403809 |
# | 10    | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 677.582336426 |
# | 65535 | 0       | 0       | 0           | 0.0           | 0.0      | 0.0    | 0.0           |
# 
# nem 1   phy BroadcastPacketAcceptTable0
# | NEM | Num Pkts Tx | Num Bytes Tx | Num Pkts Rx | Num Bytes Rx |
# | 1   | 8           | 744          | 0           | 0            |
# | 3   | 0           | 0            | 5           | 450          |
# | 4   | 0           | 0            | 2           | 164          |
# | 5   | 0           | 0            | 2           | 164          |
# | 6   | 0           | 0            | 2           | 164          |
# | 7   | 0           | 0            | 2           | 164          |
# | 8   | 0           | 0            | 2           | 164          |
# | 9   | 0           | 0            | 3           | 266          |
# | 10  | 0           | 0            | 5           | 450          |
# | 11  | 0           | 0            | 2           | 164          |
# | 24  | 0           | 0            | 2           | 164          |

import sys
import re
import os
import glob

tables = {
    "mac BroadcastPacketAcceptTable": ["Num Pkts Tx", "Num Bytes Tx",
                                       "Num Pkts Rx", "Num Bytes Rx"],
    "mac BroadcastPacketDropTable": ["Total Drops"],
    "phy BroadcastPacketAcceptTable": ["Num Pkts Tx", "Num Bytes Tx",
                                       "Num Pkts Rx", "Num Bytes Rx"]
}
#  "mac NeighborMetricTable":["NEM", "Rx Pkts", "Tx Pkts", "Missed Pkts", "BW Util", "Last Rx", "Last Tx", "SINR Avg", "SINR Stdv", "NF Avg", "NF Stdv", "Rx Rate Avg", "Tx Rate Avg"],
#  "mac NeighborStatusTable":["NEM", "Rx Pkts", "Tx Pkts", "Missed Pkts", "BW Util", "Last Rx", "Last Tx", "SINR Avg", "SINR Stdv", "NF Avg", "NF Stdv", "Rx Rate Avg", "Tx Rate Avg"],
#  "mac BroadcastPacketDropTable":["NEM", "SINR", "Reg Id", "Dst MAC", "Queue Overflow", "Bad Control", "Bad Spectrum Query", "Flow Control"],

values = {}

#nem 13  phy PathlossEventInfoTable
tbl_entry = re.compile("nem (\d+)\s+([a-z]+ [A-Za-z]+).*")
splt = re.compile("\s*\|\s*")


def print_values(key):
  global tables, values, cur_file, line

  if not values.has_key(key):
    return

  print key
  for i in range(0, len(tables[key])):
    print "  %s: " % tables[key][i],
    if type(values[key]) == list:
      print values[key][i]
    else:
      print values[key]
  print


def splitTableRow():
  global line

  ret = splt.split(line)
  ret.pop()
  ret.pop(0)
  return ret


def setupTableRead(key, default):
  global tables, values, cur_file, line

  if not values.has_key(key):
    values[key] = default

  while line and not line.startswith("|"):
    line = cur_file.readline()

  # skip the header row
  row = splitTableRow()
  if not row[0].isdigit():
    line = cur_file.readline()


def getPktInfo(key):
  global tables, values, cur_file, line

  setupTableRead(key, [0, 0, 0, 0])

  while line and line.startswith("|"):
    row = splitTableRow()
    if row[0].isdigit():
      values[key][0] += int(row[1])
      values[key][1] += int(row[2])
      values[key][2] += int(row[3])
      values[key][3] += int(row[4])

    line = cur_file.readline()


def addAllTableValues(key):
  global tables, values, cur_file, line

  setupTableRead(key, 0)

  while line and line.startswith("|"):
    row = splitTableRow()
    if row[0].isdigit():
      for r in row[1:]:
        values[key] += int(r)
    line = cur_file.readline()


def read_table():
  global tables, values, cur_file, line

  while line:
    match = tbl_entry.match(line)
    if match:
      nem_id = int(match.group(1))
      title = match.group(2)
      if title == "mac BroadcastPacketAcceptTable" or title == "phy BroadcastPacketAcceptTable":
        getPktInfo(title)
        continue

      if title == "mac BroadcastPacketDropTable":
        addAllTableValues(title)

    line = cur_file.readline()


files = glob.glob(os.path.join(sys.argv[1], "*emane-table.log"))
for fname in files:
  cur_file = open(fname, 'r')
  line = cur_file.readline()
  read_table()

print_values("mac BroadcastPacketAcceptTable")
print_values("phy BroadcastPacketAcceptTable")
print_values("mac BroadcastPacketDropTable")
