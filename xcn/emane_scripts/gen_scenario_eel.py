#!/usr/bin/env python
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

import math

# 0.0  nem:1 pathloss nem:2,50 nem:3,44 nem:4,45 
# 0.0  nem:2 pathloss nem:1,50 nem:3,44 nem:4,45 
# 0.0  nem:3 pathloss nem:1,44 nem:2,44 nem:4,50 
# 0.0  nem:4 pathloss nem:1,45 nem:2,45 nem:3,50


def gen_mesh_topo(num_nodes):
  for i in range(num_nodes):
    print "0.0  nem:%d pathloss" % (i + 1),
    for j in range(num_nodes):
      if i == j:
        continue
      print "nem:%d,20" % (j + 1),
    print


def gen_linear_topo(num_nodes):
  for i in range(num_nodes):
    print "0.0  nem:%d pathloss" % (i + 1),
    for j in range(num_nodes):
      if i == j:
        continue
      if i == (j - 1) or i == (j + 1):
        print "nem:%d,20" % (j + 1),
      else:
        print "nem:%d,999" % (j + 1),
    print


def gen_grid_topo(num_nodes):
  n = int(math.sqrt(num_nodes))
  for i in range(num_nodes):
    print "0.0  nem:%d pathloss" % (i + 1),
    for j in range(num_nodes):
      if i == j:
        continue
      if (i == (j - 1) and not (j % n) == 0) or (i == (j + 1) and not (
          (j + 1) % n) == 0):
        print "nem:%d,20" % (j + 1),
      elif i == (j - n) or i == (j + n):
        print "nem:%d,20" % (j + 1),
      else:
        print "nem:%d,999" % (j + 1),
    print


def main():
  gen_mesh_topo(4)
  print
  gen_linear_topo(4)
  print
  gen_grid_topo(12)


if __name__ == "__main__":
  main()
