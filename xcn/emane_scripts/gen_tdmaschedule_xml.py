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

from emane_xml_utils import *

#<?xml version="1.0" encoding="UTF-8"?>
#<emane-tdma-schedule>
#<structure frames="1" slots="10" slotoverhead="0" slotduration="5000" bandwidth="1M"/>
#<multiframe frequency="2.4G" power="0" class="0" datarate="100M">
#  <frame index="0">
#    <slot index="0" nodes="1"/>
#    <slot index="1" nodes="2"/>
#    <slot index="2" nodes="3"/>
#    <slot index="3" nodes="4"/>
#    <slot index="4" nodes="5"/>
#    <slot index="5" nodes="6"/>
#    <slot index="6" nodes="7"/>
#    <slot index="7" nodes="8"/>
#    <slot index="8" nodes="9"/>
#    <slot index="9" nodes="10"/>
#  </frame>
#</multiframe>
#</emane-tdma-schedule>


class tdmaschedule_xml(emane_xml_generator):

  def gen(self, params, args):
    if not params.has_key("subid"):
      error_and_exit("A subid must be specified")
    if not params.has_key("bandwidth"):
      error_and_exit("A bandwidth must be specified")
    if not params.has_key("datarate"):
      error_and_exit("A datarate must be specified")

    self.set_output(False, "tdmaschedule%d.xml" % params["subid"])

    # Validate arguments
    if len(args) != 1:
      error_and_exit("Invalid number of arguments")

    FRAMES = 1
    NODE_SLOTS = args[0]
    BANDWIDTH = params["bandwidth"]
    DATARATE = params["datarate"]

    NODES = NODE_SLOTS.keys()
    NODES.sort()
    NUM_NODES = len(NODES)
    #FREQ = "2.4G"
    FREQ = "2.347G"
    #SLOTDURATION = "1500"
    SLOTDURATION = "5000"

    # Convert NODE_SLOTS to use slots as the dictionary keys
    SLOT_NODES = {}
    for i in NODES:
      for j in NODE_SLOTS[i]:
        if not SLOT_NODES.has_key(j):
          SLOT_NODES[j] = []
        SLOT_NODES[j].append(i)

    SLOTS = SLOT_NODES.keys()
    SLOTS.sort()

    # Retrieve the max slot id
    MAX_SLOT = SLOTS[len(SLOTS) - 1]

    ets = self.add_element("emane-tdma-schedule")

    struct = self.add_element("structure", {},
                              ets,
                              frames=str(FRAMES),
                              slots=str(MAX_SLOT + 1),
                              slotoverhead="0",
                              slotduration=SLOTDURATION,
                              bandwidth=str(BANDWIDTH))

    mf = self.add_element("multiframe", {},
                          ets,
                          frequency=FREQ,
                          power="0",
                          datarate=str(DATARATE))
    mf.attrib['class'] = "0"

    for i in range(FRAMES):
      frame = self.add_element("frame", {}, mf, index=str(i))

      for j in SLOTS:
        slot = self.add_element("slot", {},
                                frame,
                                index=str(j),
                                nodes=','.join(map(str, SLOT_NODES[j])))
        self.add_element("tx", {}, slot)


def main():
  slots = {0: [2],
           1: [1, 3],
           2: [4, 5],
           3: [2],
           4: [3],
           5: [4],
           6: [1],
           7: [5],
           8: [2, 3],
           9: [1, 4]}

  params = {
    "subid":1,
    "bandwidth":100000,
    "datarate":100000
  }

  tdmaschedule_xml(".", params, slots)


if __name__ == "__main__":
  main()
