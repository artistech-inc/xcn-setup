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
import subprocess
import json
import shutil

from xcn_env import XCN_CONTAINER
from scripts.xcn_utils import *

SHIM_DIR = os.path.abspath("../../Tools/core-shim")
BUILD_MODULE = True

class XCN_SHIM(XCN_CONTAINER):

  def __init__(self, parent, params={}):
    super(self.__class__, self).__init__(parent)
    self.jar = "core-shim.jar"
    self.configfile = "core-shim.config"

    if not os.path.isdir(SHIM_DIR):
      print "Unable to find shim directory: %s" % SHIM_DIR
      os._exit(1)

    self.shim_dir = SHIM_DIR
    self.args = []

    sys.path.append(os.path.join(self.shim_dir, "bindings", "python"))

    if BUILD_MODULE:
      self.build_module()

  def build_module(self):
    print "Building Shim..."

    ret = subprocess.call("ant",
                          stdout=self.DEVNULL,
                          stderr=self.DEVNULL,
                          cwd=self.shim_dir)
    if ret != 0:
      print "Unable to build shim"
      os._exit(1)

    ret = subprocess.call("ant -f package.xml".split(),
                          stdout=self.DEVNULL,
                          stderr=self.DEVNULL,
                          cwd=self.shim_dir)
    if ret != 0:
      print "Unable to package shim"
      os._exit(1)

  def add_arg(self, arg):
    self.args.append(arg)

  def get_config(self):
    return self.config

  def add_param(self, config, key, value):
    t = type(value)

    if not config.has_key("Params"):
      config["Params"] = {}

    if t == int:
      if not config["Params"].has_key("intMap"):
        config["Params"]["intMap"] = {}
      config["Params"]["intMap"][key] = value

    elif t == float:
      if not config["Params"].has_key("dblMap"):
        config["Params"]["dblMap"] = {}
      config["Params"]["dblMap"][key] = value

    else:
      if not config["Params"].has_key("strMap"):
        config["Params"]["strMap"] = {}
      config["Params"]["strMap"][key] = value

  def write_config(self):
    configpath = os.path.join(self.get_expdir(), self.configfile)
    f = open(configpath, 'w')
    f.write(json.dumps(self.config, indent=1))
    f.close()

  def xcn_init_env(self, machine, script):
    self.jarpath = os.path.join(self.get_expdir(), self.jar)
    shutil.copyfile(os.path.join(self.shim_dir, self.jar), self.jarpath)
    if not os.path.isfile(self.jarpath):
      print "Unable to find shim jar file: %s" % self.jarpath
      os._exit(1)

    self.config = {}
    self.config["MsgType"] = "CONFIGURATION"
    self.config["ID"] = 0
    self.config["SourceModule"] = "Config"
    self.config["Nodes"] = []
    for xcn_node in self.get_nodes():
      entry = {}
      entry["Name"] = xcn_node.get_nodename()
      entry["Control"] = xcn_node.get_var("ctrl_ip")
      entry["IP"] = xcn_node.get_var("emulation_ips")
      self.config["Nodes"].append(entry)

    self.write_config()

    # Allow other modules to access this class, mainly to change configuration
    # and arguments.
    self.set_global("shim", self)

  def xcn_init_node(self, xcn_node, script):
    logfile = os.path.join(xcn_node.get_logdir(), "%s-shim.log" %
                           xcn_node.get_nodename())
    script.append_run_cmd(
        script.mk_redirect_to_file("java -jar %s -n %s -c %s %s" %
                                   (self.jar, xcn_node.get_nodename(),
                                    self.configfile, " ".join(self.args)),
                                   logfile),
        bg=True)
