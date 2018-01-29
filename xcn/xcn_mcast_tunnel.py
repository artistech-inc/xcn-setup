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

import sys
import os
import shutil
from xcn_env import XCN_CONTAINER
from scripts.xcn_utils import *

ZMQ_MCAST_DIR = os.path.abspath("../../Tools/zmq_mcast_tunnel")
BUILD_MODULE = True

class XCN_MCAST_TUNNEL(XCN_CONTAINER):

  def __init__(self, parent, mcast_addr, mcast_ports):
    super(self.__class__, self).__init__(parent)
    self.mcast_addr = mcast_addr

    self.mcast_ports = ""
    if len(mcast_ports) > 0:
      self.mcast_ports = "-p %s" % " -p ".join(map(lambda x: str(x), mcast_ports))

  def build_module(self):
    print "Building zmq_mcast_tunnel..."

    ret = subprocess.call("make",
                          stdout=self.DEVNULL,
                          stderr=self.DEVNULL,
                          cwd=ZMQ_MCAST_DIR)
    if ret != 0:
      print "Unable to build zmq_mcast_tunnel"
      os._exit(1)

  def xcn_init_env(self, machine, script):
    # We only set up tunnels if there is more than one host machine in use
    if self.get_num_machines() <= 1:
      return

    # Machine 0 will be the tunnel server
    if machine.get_machineid() == 0:
      if BUILD_MODULE:
        self.build_module()
      shutil.copy2(os.path.join(ZMQ_MCAST_DIR, "zmq_mcast_tunnel"), self.get_expdir())

    cmd = "./zmq_mcast_tunnel -s %s -m %s %s" % (machine.get_var("bridge_addr"), self.mcast_addr, self.mcast_ports)
    for m in self.get_machines():
      if m == machine:
        continue
      cmd += " -c %s" % m.get_var("bridge_addr")

    script.append_run_cmd(cmd + " -v 2>&1 > %s/zmq_mcast_tunnel.log &" % self.get_logdir())
