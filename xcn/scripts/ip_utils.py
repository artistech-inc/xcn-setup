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

import socket, struct
import math
import sys
import types
import inspect
import netifaces as ni


def validate_ip(addr):
  try:
    socket.inet_aton(addr)
    return True
  except socket.error:
    return False


def ip2int(addr):
  return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
  return socket.inet_ntoa(struct.pack("!I", int(addr)))


def get_next_ipaddr(subnet):
  global gbl_ip_utils_addrs

  if not 'gbl_ip_utils_addrs' in globals():
    gbl_ip_utils_addrs = {}

  if subnet not in gbl_ip_utils_addrs:
    val = 1
  else:
    val = gbl_ip_utils_addrs[subnet] + 1

  gbl_ip_utils_addrs[subnet] = val
  return add_addr(subnet, val)


def add_addr(ip, n):
  has_net = False
  if ip.count("/") > 0:
    has_net = True

  ipaddr = ip2int(ip.split('/')[0])
  ipaddr = int2ip(ipaddr + int(n))

  if not has_net:
    return ipaddr
  elif addressInNetwork(ipaddr, ip):
    return ipaddr
  else:
    return False


def addressInNetwork(ip, net):
  ipaddr = ip2int(ip.split('/')[0])
  netstr, bits = net.split('/')
  netaddr = ip2int(netstr)
  mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
  return (ipaddr & mask) == (netaddr & mask)


def get_subnet(ip):
  if ip.find('/') > 0:
    bits = int(ip.split('/')[1])
  else:
    bits = 32

  mask = (0xffffffff << (32 - bits)) & 0xffffffff

  ipaddr = ip2int(ip.split('/')[0])
  return "%s/%d" % (int2ip(ipaddr & mask), bits)


def size_to_netmask(size):
  return int2ip(2**32 - 2**(32 - int(size)))


def get_netmask(ip):
  if ip.find('/') < 0:
    print "ERROR: Invalid subnet (\d+.\d+.\d+.\d+/\d+)"
    return False
  size = int(ip.split('/')[1])
  return size_to_netmask(size)


def get_max_ip(subnet):
  ipaddr, mask = subnet.split("/")
  ipaddr = ip2int(ipaddr) + (
      2**32 >> int(mask)) - 2  # subtract by 2 to make room for broadcast addr
  return int2ip(ipaddr)


def get_net_size(netmask):
  binary_str = ''
  for octet in netmask.split('.'):
    binary_str += bin(int(octet))[2:].zfill(8)
  return str(len(binary_str.rstrip('0')))


def get_functions():
  myname = inspect.stack()[0][3]
  for name, t in globals().items():
    if name == myname:
      continue
    if type(t) == types.FunctionType:
      print name

def get_iface_ip(iface):
  if validate_ip(iface):
    return iface
  return ni.ifaddresses(iface)[2][0]['addr']

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "usage(): %s <function name> <arguments>" % sys.argv[0]
    get_functions()
    sys.exit(1)

  f = sys.argv[1]
  args = sys.argv[2:]

  if f == "ip2int":
    print ip2int(args[0])

  elif f == "int2ip":
    print int2ip(args[0])

  elif f == "addressInNetwork":
    print addressInNetwork(args[0], args[1])

  elif f == "get_subnet":
    print get_subnet(args[0])

  elif f == "get_net_size":
    print get_net_size(args[0])

  elif f == "get_max_ip":
    print get_max_ip(args[0])

  elif f == "add_addr":
    print add_addr(args[0], args[1])

  elif f == "size_to_netmask":
    print size_to_netmask(args[0])

  elif f == "get_netmask":
    print get_netmask(args[0])

  else:
    print "usage(): %s <function name> <arguments>" % sys.argv[0]
    sys.exit(1)
