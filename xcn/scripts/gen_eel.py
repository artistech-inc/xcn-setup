#!/usr/bin/env python
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
import math

if len(sys.argv) < 2:
  print "usage() %s <num nodes>" % sys.argv[0]
  sys.exit(1)

NUM_NODES = int(sys.argv[1])
SQRT = int(round(math.sqrt(NUM_NODES)))

for i in range(0, NUM_NODES):
  n = i + 1
  nbrs = []

  if i % SQRT != 0:
    nbrs.append(n - 1)
  if i % SQRT != SQRT - 1:
    nbrs.append(n + 1)
  if i >= SQRT:
    nbrs.append(n - SQRT)
  if i < NUM_NODES - SQRT:
    nbrs.append(n + SQRT)

  print "0.0 nem:%d pathloss" % n,
  for j in range(0, NUM_NODES):
    n = j + 1
    if i == j:
      continue
    if n in nbrs:
      print "nem:%d,0.0" % n,
    else:
      print "nem:%d,999.0" % n,
  print
