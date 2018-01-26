#!/usr/bin/env python
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
#    contributors may be used to endorse or oromote products derived from this
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
import time
import shutil
import math

from xcn_env import XCN_CONTAINER
from xcn_lxc import XCN_LXC
from xcn_docker import XCN_DOCKER
from xcn_mcast_tunnel import XCN_MCAST_TUNNEL

from scripts.xcn_utils import *
from scripts.dijkstra import *
from scripts.uxdma_tdma import *

from emane_scripts.emane_xml_utils import *
from emane_scripts.gen_platform_xml import *
from emane_scripts.gen_transvirtual_xml import *
from emane_scripts.gen_rfpipenem_xml import *
from emane_scripts.gen_rfpipemac_xml import *
from emane_scripts.gen_tdmanem_xml import *
from emane_scripts.gen_tdmaradiomodel_xml import *
from emane_scripts.gen_tdmaschedule_xml import *
from emane_scripts.gen_eventservice_xml import *
from emane_scripts.gen_eventdaemon_xml import *
from emane_scripts.gen_eelgenerator_xml import *
from emane_scripts.gen_gpsdlocationagent_xml import *

DEFAULT_RADIO = "rfpipe"
DEFAULT_BANDWIDTH = "100000"
DEFAULT_PATHLOSS_THRESHOLD = 90

CURDIR = os.path.realpath(os.path.dirname(sys.argv[0]))


class XCN_EMANE_SUBNET:
  def __init__(self, emane, subid, radio, params={}, nodes=[]):
    self.emane = emane
    self.subid = subid
    self.radio = radio
    self.params = params
    self.nodeids = []

    self.subnet_addr = self.emane.get_subnet_addr(self.subid)

    if nodes:
      self.nodeids = nodes
      self.nodes = []
      for i in self.nodeids:
        xcn_node = self.emane.get_node(i)
        if self.emane.eel_parsed:
          if not xcn_node:
            print "WARNING: Node ID %d not used in the .eel file" % (i)
        elif not self.emane.has_node(i):
          self.emane.add_node(i)

        self.nodes.append(self.emane.get_node(i))
    else:
      self.nodes = self.emane.get_nodes()
      for xcn_node in self.nodes:
        self.nodeids.append(xcn_node.get_nodeid())

    # Set defaults
    self.params["subid"] = subid
    if not self.params.has_key("bandwidth"):
      self.params["bandwidth"] = DEFAULT_BANDWIDTH
    else:
      self.params["datarate"] = self.params["bandwidth"]

    if not self.params.has_key("datarate"):
      self.params["datarate"] = DEFAULT_BANDWIDTH
    else:
      self.params["bandwidth"] = self.params["datarate"]

    if not self.params.has_key("pathloss_threshold"):
      self.params["pathloss_threshold"] = DEFAULT_PATHLOSS_THRESHOLD

    # Use precomputed if we have pathloss values, 2ray otherwise.
    if not self.params.has_key("propagationmodel") and self.emane.eel_parsed:
      if self.emane.adjacencies:
        self.params["propagationmodel"] = "precomputed"
      else:
        self.params["propagationmodel"] = "2ray"

    if self.params.has_key("frequency") and not self.params.has_key("frequencyofinterest"):
      self.params["frequencyofinterest"] = self.params["frequency"]

    self.params["otamanagergroup"] = "%s:%d" % (self.emane.get_mc(), self.emane.ota_port)
    self.params["eventservicegroup"] = "%s:%d" % (self.emane.get_mc(), self.emane.event_service_port)
    self.params["controlportendpoint"] = "0.0.0.0:%d" % (self.emane.control_port)
    self.params["otamanagerchannelenable"] = "on"

  def create_subnets(self):
    for xcn_node in self.nodes:
      if xcn_node.has_var("emane_node"):
        enode = xcn_node.get_var("emane_node")
      else:
        enode = emane_node(xcn_node.get_nodeid(), self.params)
        xcn_node.set_var("emane_node", enode)

      p = {}
      p["eventservicedevice"] = xcn_node.get_var("ctrl_interface")
      p["otamanagerdevice"] = xcn_node.get_var("ctrl_interface")

      # We allow at most 255 nodes per subnet, so each subnet's nem ids are
      # separated by 255.
      nemid = xcn_node.get_nodeid() + (255 * (self.subid-1))
      enode.add_subnet(self.subid, nemid, self.radio, self.subnet_addr, p)

  def gen_radio_xml(self):
    if self.radio == "rfpipe":
      rfpipenem_xml(self.emane.varpath, self.params)
      rfpipemac_xml(self.emane.varpath, self.params)

    elif self.radio == "tdma":
      if self.emane.get_num_machines() > 1:
	  print "WARNING: TDMA Radio is timing dependent, using multiple hosts" \
              " with this radio can massive packet loss"

      tdmanem_xml(self.emane.varpath, self.params)
      tdmaradiomodel_xml(self.emane.varpath, self.params)
      self.gen_tdma_slots()
    else:
      print "ERROR: Unknown model specified: %s" % radio
      os._exit(1)

    for xcn_node in self.nodes:
      enode = xcn_node.get_var("emane_node")

      # Store all the emulation ip addresses used by this node
      xcn_node.set_var("emulation_ips", enode.ips)

      platform_xml(self.emane.varpath, enode.params, enode)

  def gen_tdma_slots(self):
    if not self.emane.eel_parsed:
      print "ERROR: The EEL file must be parsed to generate a tdma slot schedule, set parse_eel to False"
      os._exit(1)

    nodes = set()
    nbrs = []

    for src, adj in self.emane.adjacencies[0.0].items():
      if src not in self.nodeids:
        continue

      nodes.add(src)
      for dst, pathloss in adj:
        if dst not in self.nodeids:
          continue

        nodes.add(dst)
        if pathloss < self.params["pathloss_threshold"]:
          nbrs.append((src, dst))

    utdma = UXDMA_TDMA(list(nodes), nbrs)
    tdmaschedule_xml(self.emane.varpath, self.params, utdma.colors)

  def install_static_routes(self, xcn_node, script):
    if not self.emane.eel_parsed:
      print "ERROR: The EEL file must be parsed to install static routes, set parse_eel to False"
      os._exit(1)

    enode = xcn_node.get_var("emane_node")
    if not enode.subnets.has_key(self.subid):
      return

    if not self.emane.adjacencies:
      print "WARNING: Static routes does not currently work without pathloss assigments."
      return

    nemid, radio, subnet_params = enode.subnets[self.subid]
    iface = subnet_params["device"]

    g = Graph()
    nodes = {}
    nhops = {}

    for src, adj in self.emane.adjacencies[0.0].items():
      if src not in self.nodeids:
        continue

      src_xcn_node = self.emane.get_node(src)
      if not src_xcn_node:
        print "ERROR: Unable to get node %d" % src
        sys.exit(1)
      src_enode = src_xcn_node.get_var("emane_node")
      src_ip = src_enode.get_ipaddr(self.subid)
      if src_ip is None:
        print "ERROR Retrieving source IP while installing static routes"
        os._exit(1)

      g.add_ip(src, src_ip)

      for dst, pathloss in adj:
        if dst not in self.nodeids:
          continue

        if pathloss < self.params["pathloss_threshold"]:
          g.add_edge(src, dst, 1)

          dst_xcn_node = self.emane.get_node(dst)
          if not dst_xcn_node:
            print "ERROR: Unable to get node %d" % dst
            sys.exit(1)
          dst_enode = dst_xcn_node.get_var("emane_node")
          dst_ip = dst_enode.get_ipaddr(self.subid)
          if src_ip is None:
            print "ERROR Retrieving destination IP while installing static routes"
            os._exit(1)

          g.add_ip(dst, dst_ip)
          if src == xcn_node.get_nodeid():
            nhops[dst] = (dst_ip, iface)

    for dst, nhop in dijsktra(g, xcn_node.get_nodeid())[2].items():
      if nhop == xcn_node.get_nodeid() and dst in nhops:
        nh_ip, dev = nhops[dst]
        #cmd = "route add %s dev %s" % (nh_ip, dev)
        for ip in g.ips[dst]:
          script.append_run_cmd("route add %s dev %s" % (ip, dev))
        continue

      if nhop in nhops:
        nh_ip, dev = nhops[nhop]
        for ip in g.ips[dst]:
          script.append_run_cmd("route add %s gw %s dev %s" % (ip, nh_ip, dev))


class XCN_EMANE(XCN_CONTAINER):

  def __init__(self, parent, radio, eel, params={}, gen_subnet=True, parse_eel=True):
    super(self.__class__, self).__init__(parent)

    self.eel = eel
    self.params = params
    self.adjacencies = {}
    self.positions = {}
    self.subnets = []
    self.cur_subnetid = 1
    self.using_tdma = False
    self.eel_parsed = False

    # This function will create all the nodes we need
    if parse_eel:
      self.parse_eel()
      self.eel_parsed = True

    base_port = 45000 + (self.get_runid() * 3)
    self.ota_port = base_port
    self.event_service_port = base_port + 1
    self.control_port = base_port + 2

    # Create a container module. We add it here because we need
    # the container added as a module before this module is
    # added.
    self.add_module(XCN_DOCKER(self))

    # We need multicast tunnels to get EMANE messages across multiple hosts
    # (this is no-op if we have only one machine)
    self.add_module(XCN_MCAST_TUNNEL(self, self.get_mc(), [self.ota_port, self.event_service_port, self.control_port]))

    # Register the default subnet
    if gen_subnet:
      self.add_subnet(radio, params)

  def add_subnet(self, radio, params={}, nodes=[]):
    if radio == "tdma":
      self.using_tdma = True

    subid = self.cur_subnetid
    self.cur_subnetid += 1

    subnet = XCN_EMANE_SUBNET(self, subid, radio, params, nodes)
    self.subnets.append(subnet)

  def get_mc(self):
    return "224.%d.2.8" % (self.get_runid())

  def get_ip_addr_prefix(self, subid):
    return "11.%d.%d" % (self.get_runid(), subid)

  def get_subnet_addr(self, subid):
    return "11.%d.%d.0/24" % (self.get_runid(), subid)

  def xcn_init_env(self, machine, script):
    if machine.get_machineid() != 0:
      return

    if not self.has_global("bridge_interface"):
      error_and_exit(
          "ERROR: No bridge specified for emane event service daemon")

    self.vardir = "emane_configs"
    self.varpath = os.path.join(self.get_expdir(), self.vardir)
    if os.path.isdir(self.varpath):
      print "ERROR: %s is already a directory, uanble to continue" % self.varpath

    os.makedirs(self.varpath)

    eventservice_xml(self.varpath, {
        "eventservicegroup": "%s:%d" %
                             (self.get_mc(), self.event_service_port),
        "eventservicedevice": self.get_global("bridge_interface")
    })

    eelgenerator_xml(self.varpath, {}, os.path.join(self.vardir, os.path.basename(self.eel)))

    for subnet in self.subnets:
      subnet.create_subnets()
      subnet.gen_radio_xml()

    transvirtual_xml(self.varpath)

    # Write out all the IP addresses to a file
    with open(os.path.join(self.varpath, "NODES"), 'w') as nodelist:
      for xcn_node in self.get_nodes():
        enode = xcn_node.get_var("emane_node")

        for subid in enode.subnets:
          print >> nodelist, "node:%d nem:%d subnet:%d %s" % (xcn_node.get_nodeid(), enode.get_nemid(subid), subid, enode.get_ipaddr(subid))

  def xcn_init_node(self, xcn_node, script):
    enode = xcn_node.get_var("emane_node")

    script.append_run_cmd("emane -d --logl 4 -r -f %s/emane%d.log %s/platform%d.xml" % \
           (xcn_node.get_logdir(), xcn_node.get_nodeid(), self.vardir, xcn_node.get_nodeid()), bg=True)

    gpsdlocationagent_xml(self.varpath, {}, enode)
    eventdaemon_xml(self.varpath, enode.params, enode)

    script.append_run_cmd("emaneeventd -r -d %s/eventdaemon%d.xml -l 3 -f %s/emaneeventd%d.log" %\
           (self.vardir, xcn_node.get_nodeid(), xcn_node.get_logdir(), xcn_node.get_nodeid()), bg=True)

    # This list will be used to notify olsrd which interfaces to advertise
    # over.
    xcn_node.set_var("olsrd_interfaces", enode.interfaces)

    # We add this validation to run_cmds because we want the EMANE interface to
    # finish setting up before any other module loads.
    for interface in enode.interfaces:
      script.append_run_cmd(script.mk_wait_interface(interface))

  def xcn_start_env(self, machine, script):
    if machine.get_machineid() == 0:
      # Write out the EEL file to the destination directory (with additional
      # entries for any nems created by using multiple subnets)
      new_eel = os.path.join(self.varpath, os.path.basename(self.eel))

      if self.eel_parsed:
        self.write_eel(new_eel)
      else:
        shutil.copy2(self.eel, new_eel)

    for subnet in self.subnets:
      if subnet.radio == "tdma":
        script.append_run_cmd(
	  "emaneevent-tdmaschedule %s/tdmaschedule%d.xml -g %s -p %d -i %s" %
	    (self.vardir, subnet.subid, self.get_mc(),
             self.event_service_port, self.get_global("bridge_interface")))

    script.append_run_cmd("emaneeventservice -d %s/eventservice.xml -l 3 -f %s/emaneeventservice.%d.log" %\
                   (self.vardir, self.get_logdir(), self.get_runid()))

  def install_static_routes(self, xcn_node, script):
    script.append_run_cmd(script.mk_print("Installing Static Routes on Node %d"
                                          % (xcn_node.get_nodeid())))

    for subnet in self.subnets:
      subnet.install_static_routes(xcn_node, script)

  def parse_eel(self):
    f = open(self.eel, 'r')
    nem_ids = {}
    base_nem_id = 1

    # 0.0  nem:1 pathloss nem:2,0.0 nem:3,999.0 nem:4,999.0
    pathloss_line = re.compile("(\d+\.\d+)\s+nem:(\d+)\s+pathloss\s+(.*).*")

    # 0.0  nem:1 location gps 40.031075,-74.523518,3.000000
    latlon_line = re.compile("(\d+\.\d+)\s+nem:(\d+)\s+location\s+gps\s+([^,]+),([^,]+),([^,]+).*")

    for line in f.readlines():
      match = pathloss_line.match(line)
      if match:
        timestamp = float(match.group(1))
        src = int(match.group(2))
        if src not in nem_ids:
          nem_ids[src] = base_nem_id
          base_nem_id += 1
        src = nem_ids[src]

        if not self.adjacencies.has_key(timestamp):
          self.adjacencies[timestamp] = {}

        if not self.adjacencies[timestamp].has_key(src):
          self.adjacencies[timestamp][src] = []

        if self.get_node(src) is False:
          self.add_node(src)

        for entry in match.group(3).split():
          adj = entry.replace("nem:", "").split(',')
          dst = int(adj[0])
          if dst not in nem_ids:
            nem_ids[dst] = base_nem_id
            base_nem_id += 1
          dst = nem_ids[dst]
          pathloss = float(adj[1])

          self.adjacencies[timestamp][src].append((dst, pathloss))

        continue

      match = latlon_line.match(line)
      if match:
        timestamp = float(match.group(1))
        src = int(match.group(2))
        if src not in nem_ids:
          nem_ids[src] = base_nem_id
          base_nem_id += 1
        src = nem_ids[src]

        lat = float(match.group(3))
        lon = float(match.group(4))
        alt = float(match.group(5))

        if not self.positions.has_key(timestamp):
          self.positions[timestamp] = {}

        if self.get_node(src) is False:
          self.add_node(src)

        self.positions[timestamp][src] = (lat, lon, alt)

    f.close()

  def write_eel(self, eel_path):
    f = open(eel_path, 'w')

    timestamps = self.adjacencies.keys() + self.positions.keys()
    timestamps = sorted(set(timestamps))

    for t in timestamps:
      if self.adjacencies.has_key(t):
        for src in self.adjacencies[t]:
          src_xcn_node = self.get_node(src)
          if not src_xcn_node:
            print "ERROR: Unable to get node %d" % src
            sys.exit(1)
          src_enode = src_xcn_node.get_var("emane_node")
  
          for subid in src_enode.subnets:
            src_nemid = src_enode.subnets[subid][0]
  
            found = False
            for dst, pathloss in self.adjacencies[t][src]:
              dst_xcn_node = self.get_node(dst)
	      # An invalid dst node means the node may have been removed from
	      # the eel file, the buth pathloss definition is still there.
              if not dst_xcn_node:
                continue

              dst_enode = dst_xcn_node.get_var("emane_node")
  
              if dst_enode.subnets.has_key(subid):
		# Until we have at least one entry, we don't print the header
		# for the pathloss command
                if not found:
                  print >> f, "%f nem:%d pathloss" % (t, src_nemid),
                  found = True

                dst_nemid = dst_enode.subnets[subid][0]
                print >> f, " nem:%d,%f" % (dst_nemid, pathloss),
  
            print >> f
  
      if self.positions.has_key(t):
        for src in self.positions[t]:
          src_xcn_node = self.get_node(src)
          if not src_xcn_node:
            print "ERROR: Unable to get node %d" % src
            sys.exit(1)
          src_enode = src_xcn_node.get_var("emane_node")
          lat, lon, alt = self.positions[t][src]
  
          for subid in src_enode.subnets:
            src_nemid = src_enode.subnets[subid][0]
            print >> f, "%f nem:%d location gps %f,%f,%f" % (t, src_nemid, lat, lon, alt)

  def add_node_cmd(self, nodeid, cmd):
    xcn_node = self.get_node(nodeid)

    # Replace any occurance of "IP" with the emane ip address prefix
    if type(cmd) == str:
      cmd = cmd.replace("{{IP}}", self.get_ip_addr_prefix())

    xcn_node.add_cmd(self.START_NODE, cmd)
