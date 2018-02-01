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

# <?xml version='1.0' encoding='UTF-8'?>
# <!DOCTYPE platform SYSTEM "file:///usr/share/emane/dtd/platform.dtd">
# <platform>
#   <param name="otamanagergroup" value="224.1.2.8:45702"/>
#   <param name="eventservicedevice" value="eth0"/>
#   <param name="eventservicegroup" value="224.1.2.8:45703"/>
#   <param name="otamanagerdevice" value="eth0"/>
#   <param name="controlportendpoint" value="0.0.0.0:47000"/>
#   <param name="otamanagerchannelenable" value="on"/>
#   <nem definition="rfpipenem.xml" id="1">
#     <transport definition="transvirtual.xml">
#       <param name="mask" value="255.255.255.0"/>
#       <param name="address" value="10.0.0.1"/>
#     </transport>
#   </nem>
# </platform>

class platform_xml(emane_xml_generator):
  platform_params = {
      "otamanagergroup": "224.1.2.8:45702",
      "eventservicedevice": "eth0",
      "eventservicegroup": "224.1.2.8:45703",
      "otamanagerdevice": "eth0",
      "controlportendpoint": "0.0.0.0:47000",
      "otamanagerchannelenable": "on"
  }

  transport_params = {
      "device": "emane0",
      "mask": "255.255.255.0",
      "address": "10.0.0.1",
  }

  # Args are:
  #   args[0]: Radio type (rfpipe, ieee80211abg, tdma)
  #   args[1]: Node ID (must be > 0)
  def gen(self, params, args):
    node = args[0]

    # Set defaults
    self.set_default_params("platform", self.platform_params)
    self.set_default_params("transport", self.transport_params)
    self.set_output("platform", "platform%d.xml" % node.nodeid)

    # Generate XML
    platform = self.add_element("platform", params)

    for subid in node.subnets:
      nemid, radio, params = node.subnets[subid]
      
      nem = self.add_element("nem", {},
                             platform,
                             definition="%snem%d.xml" % (radio, subid),
                             id=str(nemid))

      transport = self.add_element("transport",
                                   params,
                                   nem,
                                   definition="transvirtual.xml")


def main():
  node = emane_node(1)
  node.add_subnet(1, "rfpipe", "10.0.0.0/24", {"datarate":100000})
  node.add_subnet(2, "tdma", "10.0.1.0/24", {"datarate":5000000})
  platform_xml(".", {}, node)


if __name__ == "__main__":
  main()
