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
# <!DOCTYPE eventservice SYSTEM "file:///usr/share/emane/dtd/eventservice.dtd">
# <eventservice>
#   <param name="eventservicegroup" value="224.1.2.8:45703"/>
#   <param name="eventservicedevice" value="lxcbr.78"/>
#   <generator definition="eelgenerator.xml"/>
# </eventservice>


class eventservice_xml(emane_xml_generator):
  es_params = {
      "eventservicegroup": "224.1.2.8:45703",
      "eventservicedevice": "emanenode0",
  }

  def gen(self, params, args):
    self.set_default_params("eventservice", self.es_params)
    self.set_output("eventservice", "eventservice.xml")
    es = self.add_element("eventservice", params)
    self.add_element("generator", {}, es, definition="eelgenerator.xml")


def main():
  eventservice_xml(".", {
      "eventservicegroup": "224.1.1.1:4444",
      "eventservicedevice": "foo",
  })


if __name__ == "__main__":
  main()
