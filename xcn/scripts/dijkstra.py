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

from collections import defaultdict
import re
import sys
import os


# Based off of https://gist.github.com/econchick/4666413
class Graph:

  def __init__(self):
    self.nodes = set()
    self.edges = defaultdict(list)
    self.distances = {}
    self.ips = {}

  def add_ip(self, node, ip):
    self.nodes.add(node)
    if not self.ips.has_key(node):
      self.ips[node] = set()
    self.ips[node].add(ip)

  def add_edge(self, from_node, to_node, distance):
    self.nodes.add(from_node)
    self.nodes.add(to_node)
    self.edges[from_node].append(to_node)
    self.edges[to_node].append(from_node)
    self.distances[(to_node, from_node)] = distance
    self.distances[(from_node, to_node)] = distance
    return self


def dijsktra(graph, initial):
  visited = {initial: 0}
  path = {}
  nhop = {}

  nodes = set(graph.nodes)

  while nodes:
    min_node = None
    for node in nodes:
      if node in visited:
        if min_node is None:
          min_node = node
        elif visited[node] < visited[min_node]:
          min_node = node

    if min_node is None:
      break

    nodes.remove(min_node)
    current_weight = visited[min_node]

    for edge in graph.edges[min_node]:
      try:
        weight = current_weight + graph.distances[(min_node, edge)]
      except:
        continue
      if edge not in visited or weight < visited[edge]:
        visited[edge] = weight
        nh = min_node
        while nhop.has_key(nh) and nhop[nh] != initial:
          nh = nhop[nh]
        nhop[edge] = nh
        path[edge] = min_node

  return visited, path, nhop


def test():
  g = Graph()
  g.add_edge("1", "2", 1)
  g.add_edge("2", "3", 1)
  g.add_edge("2", "4", 1)
  g.add_edge("4", "5", 1)

  print dijsktra(g, "1")


if __name__ == "__main__":
  if len(sys.argv) <= 2:
    test()
    sys.exit(0)

  do_install = False
  if sys.argv[1] == "--install":
    do_install = True
    sys.argv.pop(1)

  base = sys.argv[1]
  CONFIG = sys.argv[2]

  try:
    f = open(CONFIG, 'r')
  except:
    print "ERROR Opening %s" % CONFIG
    sys.exit(1)

  g = Graph()
  nodes = {}
  nhops = {}

  # V9: 10.0.5.8 -> 10.0.5.7 (V8)
  nhop_line = re.compile(
      "(\S+)\((\S+)\): (\d+.\d+.\d+.\d+) -> (\d+.\d+.\d+.\d+) \((\S+)\)")
  for line in f.readlines():
    match = nhop_line.match(line)
    if match:
      n1 = match.group(1)
      dev = match.group(2)
      n1_ip = match.group(3)
      n2_ip = match.group(4)
      n2 = match.group(5)
      g.add_edge(n1, n2, 1)

      g.add_ip(n1, n1_ip)
      g.add_ip(n2, n2_ip)
      if n1 == base:
        nhops[n2] = (n2_ip, dev)

  # route add -net 10.0.0.0 netmask 255.255.0.0 gw 10.0.2.1
  for dst, nhop in dijsktra(g, base)[2].items():
    if nhop == base:
      nh_ip, dev = nhops[dst]
      #cmd = "route add %s dev %s" % (nh_ip, dev)
      for ip in g.ips[dst]:
        cmd = "route add %s dev %s" % (ip, dev)
        print cmd
        if do_install:
          os.system(cmd)
      continue

    nh_ip, dev = nhops[nhop]
    for ip in g.ips[dst]:
      cmd = "route add %s gw %s dev %s" % (ip, nh_ip, dev)
      print cmd
      if do_install:
        os.system(cmd)
