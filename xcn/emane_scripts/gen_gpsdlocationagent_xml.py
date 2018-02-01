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
#<!DOCTYPE eventagent SYSTEM "file:///usr/share/emane/dtd/eventagent.dtd">
#<eventagent library="gpsdlocationagent">
#  <param name="gpsdconnectionenabled" value="no"/>
#  <param name="pseudoterminalfile"
#         value="persist/1/var/run/gps.pty"/>
#</eventagent>


class gpsdlocationagent_xml(emane_xml_generator):
  gp_params = {
      #"gpsdconnectionenabled": "no",
      "pseudoterminalfile": "/dev/null",
  }

  def gen(self, params, args):

    # Validate arguments
    if len(args) != 1:
      error_and_exit("Invalid number of arguments")

    node = args[0]

    self.set_default_params("eventagent", self.gp_params)
    self.set_output("eventagent", "gpsdlocationagent%d.xml" % node.nodeid)
    self.add_element("eventagent", params, library="gpsdlocationagent")

def main():
  node = emane_node(1)
  gpsdlocationagent_xml(".", {}, node)


if __name__ == "__main__":
  main()
