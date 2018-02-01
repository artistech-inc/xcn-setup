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

#<?xml version='1.0' encoding='UTF-8'?>
#<!DOCTYPE mac SYSTEM 'file:///usr/share/emane/dtd/mac.dtd'>
#<mac library='tdmaeventschedulerradiomodel'>
#  <param name='fragmentcheckthreshold' value='2'/>
#  <param name='fragmenttimeoutthreshold' value='5'/>
#  <param name='neighbormetricdeletetime' value='60.0'/>
#  <param name='neighbormetricupdateinterval' value='1.0'/>
#  <param name="pcrcurveuri"
#       value='file:///usr/share/emane/xml/models/mac/tdmaeventscheduler/tdmabasemodelpcr.xml'/>
#  <param name='queue.aggregationenable' value='on'/>
#  <param name='queue.aggregationslotthreshold' value='90.0'/>
#  <param name='queue.depth' value='255'/>
#  <param name='queue.fragmentationenable' value='on'/>
#  <param name='queue.strictdequeueenable' value='off'/>
#</mac>


class tdmaradiomodel_xml(emane_xml_generator):
  mac_params = {
      "fragmentcheckthreshold": "2",
      "fragmenttimeoutthreshold": "5",
      "neighbormetricdeletetime": "60.0",
      "neighbormetricupdateinterval": "1.0",
      "pcrcurveuri":
          "file:///usr/share/emane/xml/models/mac/tdmaeventscheduler/tdmabasemodelpcr.xml",
      "queue.aggregationenable": "on",
      "queue.aggregationslotthreshold": "90.0",
      "queue.depth": "255",
      "queue.fragmentationenable": "on",
      "queue.strictdequeueenable": "off",
  }

  def gen(self, params, args):
    if not params.has_key("subid"):
      error_and_exit("A subid must be specified")

    self.set_default_params("mac", self.mac_params)
    self.set_output("mac", "tdmaradiomodel%d.xml" % params["subid"])
    self.add_element("mac", params, library="tdmaeventschedulerradiomodel")


def main():
  tdmaradiomodel_xml(".", {"subid":3})


if __name__ == "__main__":
  main()
