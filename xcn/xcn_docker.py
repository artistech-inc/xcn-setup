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

import sys
import os
import random

from xcn_env import XCN_CONTAINER, USER, OS_ID
import scripts.ip_utils as ip_utils

# Use ctrl-p ctrl-q to detach from a docker container

class XCN_DOCKER(XCN_CONTAINER):

  def __init__(self, parent):
    super(self.__class__, self).__init__(parent)

  
  # docker network create --driver bridge --subnet 10.128.0.0/24 --gateway 10.128.0.254 -o com.docker.network.bridge.name=xcn.128 xcn.128
  # docker run -v `pwd`/foo:/home -w /home --network xcn.128 -itd --name=n1 xcn
  def xcn_init_env(self, machine, script):
    self.BRIDGE = "xcn.%d" % self.get_runid()
    self.set_global("bridge_interface", self.BRIDGE)

    bridge_info = self.get_bridge_info(machine)

    self.setup_system(script)
    script.append_run_cmd("docker network create --driver bridge --subnet %s --gateway %s -o com.docker.network.bridge.name=%s %s" % (bridge_info[1], bridge_info[2], self.BRIDGE, self.BRIDGE))

    # We need to ensure we start each node on the allocated machine since
    # xcn_init_env is called once per-machine.
    for xcn_node in machine.get_nodes():
      ctrl_ip = ip_utils.get_next_ipaddr(bridge_info[1])
      name = xcn_node.get_nodename()

      xcn_node.set_access_cmd("docker exec %s" % name)
      xcn_node.set_var("ctrl_ip", ctrl_ip)
      xcn_node.set_var("ctrl_interface", "eth0")

      script.append_run_cmd("docker run --privileged -v /root:/root -v /bin:/bin -v /sbin:/sbin -v /lib:/lib -v /lib64:/lib64 -v /usr:/usr -v /etc:/etc -v `pwd`:/home -v /home/%s:/home/%s -w /home --network %s --ip %s -itd --name=%s ubuntu:%s" % (USER, USER, self.BRIDGE, ctrl_ip, name, OS_ID))

    for m in self.get_machines():
      i = m.get_machineid()
      if i != machine.get_machineid():
        script.append_run_cmd("ip route add 10.%d.%d.0/24 via %s" % (self.get_runid(), i, m.get_ipaddr()))
    
    machine.set_var("bridge_addr", bridge_info[2])

  def get_bridge_info(self, machine):
    bridge_prefix = "10.%d.%d" % (self.get_runid(), machine.get_machineid())
    bridge_mask = "%s.0/24" % bridge_prefix
    bridge_ip = ip_utils.get_max_ip(bridge_mask)
    return bridge_prefix, bridge_mask, bridge_ip

  # Disable realtime scheduling contraints
  def setup_system(self, script):
    script.append_run_cmd("sysctl kernel.sched_rt_runtime_us=-1")
    script.append_run_cmd("sysctl net.ipv4.ip_forward=1")
