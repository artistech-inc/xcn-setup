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
#<!DOCTYPE nem SYSTEM "file:///usr/share/emane/dtd/nem.dtd">
#<nem>
#  <transport definition="transvirtual.xml"/>
#  <mac definition="tdmaradiomodel.xml"/>
#  <phy>
#    <param name="fixedantennagain"         value="0.0"/>
#    <param name="fixedantennagainenable"   value="on"/>
#    <param name="bandwidth"                value="1M"/>
#    <param name="noisemode"                value="all"/>
#    <param name="propagationmodel"         value="precomputed"/>
#    <param name="systemnoisefigure"        value="4.0"/>
#    <param name="subid"                    value="7"/>
#    <param name="frequency"                value="2347000000"/>
#    <param name="frequencyofinterest"      value="2347000000"/>
#  </phy>
#</nem>


class tdmanem_xml(emane_xml_generator):
  phy_params = {
      "subid": "7",
      "bandwidth": "1M",
      "propagationmodel": "precomputed",
      "fixedantennagainenable": "on",
      "fixedantennagain": "0.0",
      "systemnoisefigure": "4.0",
      "noisemode": "outofband",
      "frequency": "2347000000",
      "frequencyofinterest" :"2347000000",
  }

  def gen(self, params, args):
    if not params.has_key("subid"):
      error_and_exit("A subid must be specified")

    self.set_default_params("phy", self.phy_params)
    self.set_output("nem", "tdmanem%d.xml" % params["subid"])

    self.add_element("nem")
    self.add_element("transport", definition="transvirtual.xml")
    self.add_element("mac", definition="tdmaradiomodel%d.xml" % params["subid"])
    self.add_element("phy", params)


def main():
  tdmanem_xml(".", {"subid":1})


if __name__ == "__main__":
  main()
