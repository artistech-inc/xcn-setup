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
import copy
sys.path.append('..')

from scripts.ip_utils import *
from scripts.xcn_utils import *


# converts a list of "key:value" strings to a dictionary
def params_from_args(args):
  params = {}

  if len(args) <= 1:
    return

  for entry in args:
    if entry.count(":") != 1:
      error_and_exit("Unable to parse %s" % entry)

    key, value = entry.split(":")

    if key not in params:
      error_and_exit("%s not found in parameter list" % key)

    params[key] = value

  return params


def merge_params(cur, new):
  ret = {}
  if type(new) == str:
    new = params_from_args(new)

  if type(new) != dict:
    error_and_exit("Parameters must be in a dictionary", 2)

  for k, v in cur.items():
    if new.has_key(k):
      ret[k] = new[k]
    else:
      ret[k] = v

  return ret


class emane_node:
  def __init__(self, nodeid, params={}):
    self.nodeid = int(nodeid)
    self.params = params
    self.subnets = {}
    self.ips = []
    self.interfaces = []

  def add_subnet(self, subid, nemid, radio, addr, params):
    if radio not in ["rfpipe", "ieee80211abg", "tdma"]:
      error_and_exit("Invalid radio type: %s" % radio)

    subnet_params = copy.deepcopy(self.params)
    subnet_params.update(params)
    subnet_params["subid"] = subid
    subnet_params["mask"] = get_netmask(addr)
    subnet_params["address"] = get_next_ipaddr(addr)
    subnet_params["device"] = "emane%d" % subid

    self.subnets[subid] = (nemid, radio, subnet_params)

    self.ips.append(subnet_params["address"])
    self.interfaces.append(subnet_params["device"])

  def get_ipaddr(self, subid):
    if not self.subnets.has_key(subid):
      return None
    return self.subnets[subid][2]["address"]

  def get_nemid(self, subid):
    if not self.subnets.has_key(subid):
      return None
    return self.subnets[subid][0]

  def get_subnet_interface(self, subid):
    if not self.subnets.has_key(subid):
      return None
    return self.subnets[subid][2]["device"]

  def get_subnet_params(self, subid):
    if not self.subnets.has_key(subid):
      return None
    return self.subnets[subid][2]

  def get_subnet_radio(self, subid):
    if not self.subnets.has_key(subid):
      return None
    return self.subnets[subid][1]

class emane_xml_generator:

  def __init__(self, outdir, params={}, *args):
    self.default_params = {}
    self.root = False

    if not os.path.isdir(outdir):
      error_and_exit("ERROR: %s is not a directory" % outdir)
    self.outdir = outdir

    self.gen(params, args)
    self.print_xml()

  def set_default_params(self, tag, params):
    self.default_params[tag] = {}
    for k, v in params.items():
      self.default_params[tag][k] = v

  def set_output(self, doctype, outputFileName=False):
    self.doctype = doctype
    self.outputFileName = os.path.join(self.outdir, outputFileName)

  def add_element(self, tag, params={}, parent=False, **args):
    if parent is False and self.root is False:
      self.root = etree.Element(tag, args)
      node = self.root

    elif parent is False:
      node = etree.SubElement(self.root, tag, args)

    else:
      node = etree.SubElement(parent, tag, args)

    if self.default_params.has_key(tag):
      params = merge_params(self.default_params[tag], params)

      for k, v in params.items():
        etree.SubElement(node, "param", name=str(k), value=str(v))

    return node

  def gen(self, params, args):
    traceback.print_stack()
    print "ERROR: This function must be overridden"
    sys.exit(1)

  def print_xml(self):
    if not self.outputFileName:
      out = sys.stdout
    else:
      out = open(self.outputFileName, 'w')

    if self.doctype:
      doctype = '<!DOCTYPE %s SYSTEM ' % (
          self.doctype) + '"file:///usr/share/emane/dtd/%s.dtd">' % (
              self.doctype)
    else:
      doctype = ''

    out.write(etree.tostring(self.root,
                             xml_declaration=True,
                             encoding="UTF-8",
                             doctype=doctype,
                             pretty_print=True))
