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
import glob
import socket
import inspect
import subprocess
import netifaces
from lxml import etree


def error_and_exit(msg, stack_level=1):
  print "%s: %s" % (inspect.stack(2)[stack_level][1], msg)
  sys.exit(1)


def test_int(i):
  try:
    return int(i)
  except ValueError:
    error_and_exit("%s is not an integer" % i, 2)


def rm_files(paths):
  if type(paths) is not list:
    paths = [paths]

  for path in paths:
    for f in glob.glob(path):
      if os.path.isfile(f):
        os.remove(f)


def recursive_chown(path, uid, gid):
  os.chown(path, uid, gid)
  for item in os.listdir(path):
    itempath = os.path.join(path, item)
    if os.path.isfile(itempath):
      os.chown(itempath, uid, gid)
    elif os.path.isdir(itempath):
      os.chown(itempath, uid, gid)
      recursive_chown(itempath, uid, gid)


def write_shell_script(path):
  script = open(path, 'w')
  print >> script, '#!/bin/bash'
  print >> script
  print >> script, 'if [ $EUID -ne 0 ]; then'
  print >> script, '  exec sudo "$0" "$@"'
  print >> script, 'fi'
  print >> script

  os.chmod(path, 0o744)

  return script


def scp_recursive(ip, path, dest=False):
  if not os.path.isdir(path) and not os.path.isfile(path):
    print "ERROR: Path not found: %s" % path
    os._exit(1)

  if dest is False:
    dest = path

  cmd = "scp -q -r %s %s:%s" % (path, ip, dest)
  cmd = cmd.strip()

  p = subprocess.Popen(cmd.split())

  streamdata = p.communicate()[0]
  if p.returncode != 0:
    print "ERROR running command %s" % cmd
    os._exit(p.returncode)


def get_iface(ip):
  ip = socket.gethostbyname(ip)

  for iface in netifaces.interfaces():
    try:
      addr = netifaces.ifaddresses(iface)[2][0]['addr']
      if addr == ip:
        return iface
    except:
      pass


def get_primary_iface():
  for iface in netifaces.interfaces():
    if iface.startswith("lo") or iface.startswith("lxc") or iface.startswith("br") or iface.startswith("veth"):
      continue
    try:
      addr = netifaces.ifaddresses(iface)[2][0]['addr']
      return iface, addr
    except:
      pass


def has_ipaddr(ip):
  for iface in netifaces.interfaces():
    try:
      addr = netifaces.ifaddresses(iface)[2][0]['addr']
      if addr == ip:
        return True
    except:
      pass

  return False
