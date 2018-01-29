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
import random

from xcn_env import XCN_CONTAINER, USER
import scripts.ip_utils as ip_utils


class XCN_LXC(XCN_CONTAINER):

  def __init__(self, parent):
    super(self.__class__, self).__init__(parent)

  def xcn_init_env(self, machine, script):
    self.BRIDGE = "lxcbr.%d" % self.get_runid()
    bridge_info = self.get_bridge_info(machine)

    self.setup_system(script)
    self.create_bridge(script, bridge_info)

    # We need to ensure we start each node on the allocated machine since
    # xcn_init_env is called once per-machine.
    for xcn_node in machine.get_nodes():
      self.start_lxc(xcn_node, script)

    self.set_global("bridge_interface", self.BRIDGE)

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

  def xcn_init_node(self, xcn_node, script):
    bridge_info = self.get_bridge_info(xcn_node.get_machine())

    script.append_run_cmd("route add default gateway %s eth0" % (bridge_info[2]))
    script.append_run_cmd("ip route del 10.0.0.0/8")

  # Disable realtime scheduling contraints
  def setup_system(self, script):
    script.append_run_cmd("sysctl kernel.sched_rt_runtime_us=-1")
    script.append_run_cmd("sysctl net.ipv4.ip_forward=1")

  # Commands to create a bridge for messages between LXCs
  def create_bridge(self, script, bridge_info):
    #iface = self.get_primary_iface()
    #vlan = "%s.%d" % (iface, self.get_runid())
    #script.append_run_cmd("ip link add link %s name %s type vlan id %d" % (iface, vlan, self.get_runid()))
    script.append_run_cmd("brctl addbr %s" % self.BRIDGE)
    script.append_run_cmd("brctl setfd %s 0" % self.BRIDGE)
    #script.append_run_cmd("brctl addif %s %s.%d" % (self.BRIDGE, iface, self.get_runid()))
    script.append_run_cmd(script.mk_wait_interface(self.BRIDGE))
    #script.append_run_cmd("ip link set %s up" % vlan)
    script.append_run_cmd("")
    script.append_run_cmd("ip addr add %s dev %s" % (bridge_info[2], self.BRIDGE))
    script.append_run_cmd("ifconfig %s broadcast %s.255 netmask 255.255.255.0" % (self.BRIDGE, bridge_info[0]))
    script.append_run_cmd("ip link set %s up" % self.BRIDGE)
    #script.append_run_cmd("iptables -t nat -A POSTROUTING -s %s ! -d %s -j MASQUERADE" % (bridge_info[1], bridge_info[1]))
    #script.append_run_cmd("iptables -I INPUT -i %s -j ACCEPT" % self.BRIDGE)
    #script.append_run_cmd("iptables -I FORWARD -i %s -j ACCEPT" % self.BRIDGE)

  # This function will create a node specific lxc.conf file. It will also set
  # the "ctrl_ip" variable in each node's private dictionary.
  def start_lxc(self, xcn_node, script):
    bridge_info = self.get_bridge_info(xcn_node.get_machine())
    ctrl_ip = ip_utils.get_next_ipaddr(bridge_info[1])

    lxc_file = open(
        os.path.join(self.get_expdir(), xcn_node.get_vardir(), "lxc.conf"), 'w')

    xcn_node.set_var("ctrl_ip", ctrl_ip)

    #xcn_node.set_access_cmd("ssh -i ${HOME}/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s@%s -- " % (USER, ctrl_ip))
    xcn_node.set_access_cmd("lxc-attach -n %s --" % xcn_node.get_nodename())

    nodehex = "%08x" % ip_utils.ip2int(ctrl_ip)
    nodehwaddr = "%s:%s:%s:%s" % \
                 (nodehex[0:2],nodehex[2:4],nodehex[4:6],nodehex[6:8])

    print >> lxc_file, "lxc.utsname=%s" % xcn_node.get_nodename()
    print >> lxc_file, "lxc.network.type=veth"
    print >> lxc_file, "lxc.network.name=eth0"
    print >> lxc_file, "lxc.network.flags=up"
    print >> lxc_file, "lxc.network.link=%s" % self.BRIDGE
    print >> lxc_file, "lxc.network.hwaddr=02:01:%s" % nodehwaddr
    print >> lxc_file, "lxc.network.ipv4=%s" % ctrl_ip
    print >> lxc_file, "lxc.network.veth.pair=veth0.%d.%d" % (
        xcn_node.get_nodeid(), self.get_runid())
    #print >> lxc_file
    #print >> lxc_file, "lxc.network.type=veth"
    #print >> lxc_file, "lxc.network.name=eth1"
    #print >> lxc_file, "lxc.network.hwaddr=02:02:%s" % nodehwaddr
    #print >> lxc_file, "lxc.network.veth.pair=veth1.%d.%d" % (
    #    xcn_node.get_nodeid(), self.get_runid())
    print >> lxc_file
    print >> lxc_file, "lxc.network.type = empty"
    print >> lxc_file, "lxc.network.flags=up"
    print >> lxc_file
    print >> lxc_file, "lxc.console = none"
    print >> lxc_file, "lxc.tty = 1"
    print >> lxc_file, "lxc.pts = 128"
    print >> lxc_file, "lxc.cgroup.devices.allow = a"
    print >> lxc_file
    print >> lxc_file, "lxc.autodev = 0"
    print >> lxc_file
    print >> lxc_file, "lxc.aa_profile = unconfined"

    xcn_node.set_var("ctrl_interface", "eth0")

    script.append_run_cmd(
        "nohup lxc-execute -f %s/lxc.conf -n %s -o %s/lxc-execute.log -- $(which sshd) &> /dev/null || exit 1"
        % (xcn_node.get_vardir(), xcn_node.get_nodename(),
           xcn_node.get_logdir()),
        bg=True)

    script.append_validate_cmd(script.mk_wait_file("%s/lxc-execute.log" %
                                                   xcn_node.get_logdir()))

