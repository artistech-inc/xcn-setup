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
from xcn_env import XCN_CONTAINER
from scripts.xcn_utils import *

class XCN_OLSRD(XCN_CONTAINER):

  def __init__(self, parent, params={}):
    super(self.__class__, self).__init__(parent)
    self.sleep_warn = True
    pass

  def xcn_init_node(self, xcn_node, script):
    if not xcn_node.has_var("olsrd_interfaces"):
      return

    interfaces = " ".join(xcn_node.get_var("olsrd_interfaces"))
    script.append_run_cmd(script.mk_redirect_to_file("olsrd -d 1 -i %s" % interfaces, 
			  "%s/%s.olsrd.out" % (xcn_node.get_logdir(),
			  xcn_node.get_nodename()), bg=True))

  def xcn_start_node(self, xcn_node, script):
    if self.sleep_warn:
      script.append_run_cmd("echo 'Sleeping 30 seconds to allow OLSRD to build routes'")
      self.sleep_warn = False

    script.append_run_cmd(script.mk_sleep(30000))
