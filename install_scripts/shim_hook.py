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

import os
import fcntl
import sys
import select
import Queue
import subprocess
import threading
import random

from xcn_env import XCN_ENVIRONMENT
from xcn_lxc import XCN_LXC
from xcn_emane import XCN_EMANE
from xcn_shim import XCN_SHIM

# Shim bindings path
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_DIR, "../../Tools/core-shim/bindings/python/"))

from shim_bindings import *
from data_msg import *


class ShimHook:

  def __init__(self, datarate, eel_file, radio='rfpipe', machines=[]):
    # Holds connections to the shim nodes in the XCN environment. These
    # connections are created as necessary.
    self.shim_hooks = {}

    # Queue for pushing Shim modules to the select thread
    self.queue = Queue.Queue()

    # Internal TCP Socket to wakeup the select thread.
    self.pipefd = os.pipe()
    fcntl.fcntl(self.pipefd[0], fcntl.F_SETFL, os.O_NONBLOCK)

    # Start the select thread
    thread = threading.Thread(target=self.select_thread)
    thread.start()

    # XCN Environment
    self.xcn_env = XCN_ENVIRONMENT()

    if machines:
      self.xcn_env.set_machines(machines)

    # EMANE
    self.emane = XCN_EMANE(self.xcn_env, radio, eel_file,
                           {"datarate": datarate,})
    self.num_nodes = self.emane.get_num_nodes()

    # We need time to set up EMANE
    self.emane.set_init_time(self.num_nodes)

    # Add all modules to the xcn environment in order we want them to run.
    self.xcn_env.add_module(self.emane)
    self.emane.add_module(XCN_SHIM(self.emane))

    # Install static routes into the scenario
    self.emane.add_cmd("xcn_init_node", self.emane.install_static_routes)

    # Start tcpdump on all nodes
    self.emane.add_cmd("xcn_init_node", "tcpdump -i emane0 -w {{LOGDIR}}/{{NODENAME}}-tcpdump.out &> /dev/null &")

    # Run the experiment
    self.xcn_env.start()

  def connect_to_shim(self, nodeid):
    if nodeid > self.num_nodes or nodeid <= 0:
      print "ERROR: Invalid Node ID: %d" % nodeid
      os._exit(1)

    if self.shim_hooks.has_key(nodeid):
      return

    xcn_node = self.emane.get_node(nodeid)
    module = ShimModule("ShimHook", 9999, xcn_node.get_var("ctrl_ip"))
    module.connect_tcp()
    self.shim_hooks[nodeid] = module

    # notify the select thread of the new socket
    try:
      self.queue.put(module)
      os.write(self.pipefd[1], "0")
    except:
      print "ERROR Sending new connection to select thread"
      os._exit(1)

  def select_thread(self):
    tcp_conns = {}
    readfds = [self.pipefd[0]]

    while True:
      readable, writable, exception = select.select(readfds, [], readfds)

      # check for errors and remove closed sockets
      for sock in exception:
        if sock in tcp_conns:
          module = tcp_conns[sock]
          tcp_conns.pop(sock)
          readfds.remove(sock)
          module.close_server()
          sock.close()
        else:
          print "ERROR: Invalid socket exception"
          os._exit(1)

      for sock in readable:
        if sock is self.pipefd[0]:
          try:
            os.read(self.pipefd[0], 1024)
          except:
            print "ERROR in os.read"
            os._exit(1)

# Read all items from the queue. Once the queue is empty (queue.get
# raises an Empty exception), we break out of this while loop
          while True:
            try:
              module = self.queue.get(False)
            except:
              break

            tcp_conns[module.tcp] = module
            readfds.append(module.tcp)

            self.queue.task_done()

        # Messages from the Shim Nodes. See @transmit.
        if sock in tcp_conns:
          module = tcp_conns[sock]
          try:
            msg, atime = module.read_incoming(1)[0]
          except:
            module.close_server()
            tcp_conns.pop(sock)
            readfds.remove(sock)
            sock.close()
            continue

          addr = getMeta(msg, "ShimHookCallbackIP")
          port = getMeta(msg, "ShimHookCallbackPort")
          meta = getParam(msg, "ShimHookMeta")

          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s.connect((addr, port))
          s.send(meta)

  def transmit(self, src_node_id, dst_node_id, size, callback_ip, callback_port,
               meta):
    # The connect calls are NO-OP if we already have a connection
    self.connect_to_shim(src_node_id)
    self.connect_to_shim(dst_node_id)

    src_module = self.shim_hooks[src_node_id]
    dst_name = self.emane.get_node(dst_node_id).get_nodename()

    # Create a data packet. The packet's size will be effected by the "meta"
    # variable, but not the callback variables
    msg = create_data("ShimHook", dst_name)
    setSize(msg, size)

    # Set reliable bit for the message so we know it'll be delivered.
    setReliable(msg)

    addParam(msg, "ShimHookMeta", meta)
    addMeta(msg, "ShimHookCallbackIP", callback_ip)
    addMeta(msg, "ShimHookCallbackPort", callback_port)

    # Send the message to the Shim Node
    src_module.send_to_shim(msg)

  def stop(self, collect=True):
    cmds = [os.path.join(CUR_DIR, "kill.sh")]
    if collect:
      cmds.append("-c")

    cmds.append(str(self.xcn_env.get_runid()))

    output = subprocess.Popen(cmds, stdout=subprocess.PIPE).communicate()[0]

    output_dir = output.strip().replace("Output saved to ", "")

    return output_dir


def main():
  num_packets = 100

  # Use 1Mbps Network
  shim = ShimHook(1000000, "test.eel")

  # test socket
  addr = "127.0.0.1"
  port = 43212
  try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((addr, port))
    server.listen(1)
  except:
    print "ERROR Creating Test Server"
    os._exit(1)

  for i in range(num_packets):
    shim.transmit(
        random.randint(1, 3), random.randint(1, 3), 10000, addr, port,
        "MESSAGE %d" % i)

  for i in range(num_packets):
    try:
      conn, addr = server.accept()
      data = conn.recv(65535)
      print "Received: %s (%d out of %d)" % (data, i + 1, num_packets)
      conn.close()
    except:
      print "ERROR Retrieving Test Message"
      os._exit(1)

  server.close()

  out = shim.stop(True)
  print "Output Directory: %s" % out

  os._exit(0)


if __name__ == "__main__":
  main()
