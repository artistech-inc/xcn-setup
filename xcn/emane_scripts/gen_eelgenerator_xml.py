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

# <?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE eventgenerator SYSTEM "file:///usr/share/emane/dtd/eventgenerator.dtd">
# <eventgenerator library="eelgenerator">
#     <param name="inputfile" value="scenario.eel" />
#     <paramlist name="loader">
#       <item value="commeffect:eelloadercommeffect:delta"/>
#       <item value="location,velocity,orientation:eelloaderlocation:delta"/>
#       <item value="pathloss:eelloaderpathloss:delta"/>
#       <item value="antennaprofile:eelloaderantennaprofile:delta"/>
#     </paramlist>
# </eventgenerator>


class eelgenerator_xml(emane_xml_generator):

  def gen(self, params, args):
    # Validate arguments
    if len(args) != 1:
      error_and_exit("Invalid number of arguments")

    inputfile = args[0]
    self.set_output("eventgenerator", "eelgenerator.xml")
    self.set_default_params("eventgenerator", {"inputfile": inputfile})

    eg = self.add_element("eventgenerator", library="eelgenerator")

    plist = self.add_element("paramlist", {}, eg, name="loader")
    self.add_element("item", {},
                     plist,
                     value="commeffect:eelloadercommeffect:delta")
    self.add_element(
        "item", {},
        plist,
        value="location,velocity,orientation:eelloaderlocation:delta")
    self.add_element("item", {},
                     plist,
                     value="pathloss:eelloaderpathloss:delta")
    self.add_element("item", {},
                     plist,
                     value="antennaprofile:eelloaderantennaprofile:delta")


def main():
  eelgenerator_xml(".", {}, "scenario.eel")


if __name__ == "__main__":
  main()
