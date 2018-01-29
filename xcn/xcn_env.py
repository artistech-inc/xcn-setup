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
import time
import subprocess
import signal
import pwd
import grp
import scripts.ip_utils as ip_utils
import scripts.xcn_utils as xcn_utils
import socket
import platform

USER = os.environ["USER"]
if os.environ.has_key("SUDO_USER"):
  USER = os.environ['SUDO_USER']

USER_UID = pwd.getpwnam(USER).pw_uid
USER_GID = grp.getgrnam(USER).gr_gid

SYSTEM_TYPE = platform.system()
if SYSTEM_TYPE == 'Linux':
  OS_NAME, OS_VERSION, OS_ID = platform.linux_distribution()
else:
  print "ERROR: Untested Operating System"
  sys.exit(1)

def signal_handler(signal, frame):
  print "Experiment ended by user input"
  os._exit(1)

# We will create four sets of scripts in this function. Commands will use the
# following formats:
#
#    "string command"
#    function
#
# Any class/function provided as a command must take the parameters (xcn_env,
# run_cmds, validate_cmds). The first parameter is a pointer to the
# XCN_ENVIRONMENT class, allowing the function to access information about the
# environment and each node. The second argument (run_cmd) is a list of
# commands. The function is expected to append it's commands to this list of
# commands. This list will later be converted into a bash script and run. The
# validate_cmds is also a list of commands the function should append to. This
# will also be converted into a bash script and run immediately after the
# "run_cmd" generated script finishes. The purpose of the "validate_cmd"
# generated script is to validate all commands in the "run_cmd" script executed
# successfully.
#
# Note if a single string command is given in lieu of a function, it will be
# appended to the "run_cmd" list of commands. The following tokens will be
# replace with the given variable:
#   {{RUNID}} - replaced with xcn_env.get_runid()
#   {{EXPDIR}} - replaced with xcn_env.get_expdir()
#   {{VARDIR}} - replaced with xcn_node.get_vardir()
#   {{LOGDIR}} - replaced with xcn_node.get_logdir()
#   {{NODENAME}} - replaced with xcn_node.get_nodename()
#   {{NODEID}} - replaced with xcn_node.get_nodeid()
#
# The four sets of scripts are grouped as follows:
#
#  __init_env_scripts: These scripts are run to start the experiment environment (i.e.
#  starting lxc containers or VMs).
#
#  __init_node_scripts: These scripts are run once per xcn_node after any validation
#  scripts in the environment have been run. 
#
#    Node commands will always be prepended with xcn_node.ACCESS_CMD. The purpose
#    of this variable is to provide access into a node, such as running an ssh
#    command or lxc-attach.
#
#  __start_env_scripts: These scripts run immediately after all of the __init_node_scripts
#  have returned.
#
#  __start_node_scripts: These scripts run immediately after all of the __start_env_scripts
#  have returned. Like node scripts, these commands will always be prepended
#  with xcn_node.ACCESS_CMD.
#
#  __stop_node_scripts: TODO
#
#  __stop_env_scripts: These scripts are executed on xcn_env.get_expdir() after the
#  experiment has been halted and the environment torn down. An example usage
#  of this type of script is to automatically parse data after an experiment
#  has finished.


class XCN_CONTAINER(object):

  # We use a list to hold variables so all modules can have a pointer to the
  # same variable.
  def __init__(self, parent, params={}):
    self.parent = parent
    self.xcn_nodes = [{}]

    if parent:
      self.used_ids = parent.used_ids
      self.count = parent.count
    else:
      self.used_ids = [[]]
      self.count = [0]

  def __getattr__(self, attr):

    # Raise an except here if we don't have a parent set or for function names
    # starting with '__' or 'xcn'. We intentionally do not want to inherit
    # these functions from our parent because the former are considered private
    # functions and the later must explicitly created by each module/container.
    if not self.parent or attr.startswith("__") or attr.startswith("xcn"):
      raise AttributeError("'%s' object has no attribute '%s'" %
                           (type(self), attr))

    try:
      orig_attr = self.parent.__getattribute__(attr)
      if callable(orig_attr):

        def wrapper(*args, **kwargs):
          return orig_attr(*args, **kwargs)

        return wrapper
      else:
        return orig_attr
    except:
      return self.parent.__getattr__(attr)

  def __test_recur(self):
    return not self.parent or len(self.xcn_nodes[0]) > 0

  def has_node(self, nodeid):
    if self.__test_recur():
      return self.xcn_nodes[0].has_key(nodeid)
    return self.parent.has_node(nodeid)

  def check_valid_nodeid(self, nodeid):
    if nodeid in self.used_ids[0]:
      return False
    return True

  def get_next_nodeid(self):
    while not self.check_valid_nodeid(self.count[0]):
      self.count[0] += 1
    return self.count[0]

  def add_node(self, nodeid=False):
    if nodeid is False:
      nodeid = self.get_next_nodeid()
    elif not self.check_valid_nodeid(nodeid):
      raise ValueError(
          "Attempting to assign node ID %d twice (node IDs must be unique)" %
          nodeid)

    new_node = XCN_NODE(self, nodeid)
    self.xcn_nodes[0][nodeid] = new_node
    self.used_ids[0].append(nodeid)
    self.add_node_to_machine(new_node)
    return new_node

  def add_nodes(self, num):
    for i in range(num):
      self.add_node()
    return self.get_nodes()

  # This function will merge each module's nodes
  def share_nodes(self, module):
    module.xcn_nodes[0].update(self.xcn_nodes[0])
    self.xcn_nodes = module.xcn_nodes

  def get_node(self, nodeid):
    if self.xcn_nodes[0].has_key(nodeid):
      return self.xcn_nodes[0][nodeid]
    if not self.parent:
      return False
    return self.parent.get_node(nodeid)

  def get_nodes(self):
    if self.__test_recur():
      return self.xcn_nodes[0].values()
    return self.parent.get_nodes()

  def get_num_nodes(self):
    if self.__test_recur():
      return len(self.xcn_nodes[0])
    return self.parent.get_num_nodes()


# This class contains all necessary information for an experiment run. It does
# not contain any module specific information, such as whether we use LXC or a
# VM, EMANE or NS3, etc...
class XCN_ENVIRONMENT(XCN_CONTAINER):

  # "enum" for script types
  INIT_ENV = "xcn_init_env"
  INIT_NODE = "xcn_init_node"
  START_ENV = "xcn_start_env"
  START_NODE = "xcn_start_node"
  STOP_NODE = "xcn_stop_node"
  STOP_ENV = "xcn_stop_env"

  def __init__(self, global_attrs={}):
    super(self.__class__, self).__init__(False, global_attrs)

    # Add signal handler to catch ctrl-c cleanly
    signal.signal(signal.SIGINT, signal_handler)

    # Helper for piping to /dev/null
    self.DEVNULL = open('/dev/null', 'w')

    # Private dictionary for global experiment variables, should be only
    # accessed with the getter/setter functions.
    self.__globals = {}

    # Create a run id. This value may be over written below.
    self.__RUNID = random.randint(1, 254)
    self.set_expdir(os.path.join(os.path.sep, "tmp", "xcn"))

    self.set_duration(-1)
    self.set_init_time(-1)

    # Set all global attributes to lower case and parse certain ones
    for key, value in global_attrs.items():
      if type(key) is str:
        key = key.lower()
        if key == "duration":
          self.set_duration(value)
          continue
        if key == "init_time":
          self.set_init_time(value)
          continue
        if key == "runid":
          self.__RUNID = int(value)
          continue
        if key == "expdir" or key == "exp_dir":
          self.set_expdir(int(value))
          continue

      self.__globals[key] = value

    if self.get_runid() <= 0 or self.get_runid() >= 255:
      print "ERROR: RUNID must be > 0 and < 255"
      os._exit(1)

    # Append the RUNID to the output directory
    self.set_expdir("%s.%d" % (self.get_expdir(), self.get_runid()))

    if os.path.isdir(self.get_expdir()):
      print "ERROR: %s is already a directory, unable to continue" % self.get_expdir(
      )
      os._exit(1)

    os.makedirs(self.get_expdir())
    print "Created scenario directory: %s" % self.get_expdir()

    self.set_logdir("logs")
    os.makedirs(os.path.join(self.get_expdir(), self.get_logdir()))

    self.MODULES = set()
    self.COMMANDS = {}
    self.COMMANDS[self.INIT_ENV] = []
    self.COMMANDS[self.START_ENV] = []
    self.COMMANDS[self.STOP_ENV] = []

    self.__MACHINES = [XCN_MACHINE(self, 0, "localhost")]

  def set_machines(self, hosts):
    self.__MACHINES = []

    # ensure the given list has unique ip address (not hostname) values
    ips = []
    seen = set()
    
    for host in hosts:
      ip = socket.gethostbyname(host)
      if ip in seen:
        continue
      ips.append(ip)
      seen.add(ip)
      
    # If we have more than one IP address, we will look for any localhost
    # address listed in the ips set. If we find one, then we will convert that
    # address to the address of the interface used to route to another machine
    # in the ips list.
    if len(ips) > 1:
      for i in range(len(ips)):
        if ips[i] == '127.0.0.1':
          if i == 0:
            n = i + 1
          else:
            n = i - 1
          break

      # connect to another given machine's ssh port. SSH is required to run
      # across multiple machines, so we know this port is open.
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect((ips[n],22))
      ips[i] = s.getsockname()[0]
      s.close()

      self.set_primary_iface(xcn_utils.get_iface(ips[i]))

    for i in range(len(ips)):
      self.__MACHINES.append(XCN_MACHINE(self, i, ips[i]))

  def get_primary_iface(self):
    return self.__primary_iface

  def set_primary_iface(self, iface):
    self.__primary_iface = iface

  def get_machines(self):
    return self.__MACHINES

  def get_num_machines(self):
    return len(self.get_machines())

  def add_node_to_machine(self, xcn_node):
    prev = self.get_machines()[0]
    p = len(prev.get_nodes())
    for i in range(1, self.get_num_machines()):
      machine = self.get_machines()[i]
      m = len(machine.get_nodes())
      if m < p:
        machine.add_node(xcn_node)
        xcn_node.add_machine(machine)
        return
      prev = machine
      p = m

    machine = self.get_machines()[0]
    machine.add_node(xcn_node)
    xcn_node.add_machine(machine)

  def set_duration(self, value):
    self.__DURATION = int(value)

  def get_duration(self):
    return self.__DURATION

  def set_init_time(self, value):
    self.__INIT_TIME = int(value)

  def get_init_time(self):
    return self.__INIT_TIME

  def get_runid(self):
    return self.__RUNID

  def get_all_nodes(self):
    nodes = set()
    for module in self.MODULES:
      nodes.update(module.get_nodes())

    return nodes

  def set_expdir(self, value):
    self.__EXPDIR = value

  def get_expdir(self):
    return self.__EXPDIR

  def set_vardir(self, value):
    self.__VARDIR = value

  def get_vardir(self):
    return self.__VARDIR

  def set_logdir(self, value):
    self.__LOGDIR = value

  def get_logdir(self):
    return self.__LOGDIR

  # Function to start an experiment. This function will set up the
  # XCN_ENVIRONMENT class and then create the various scripts we'll run. These
  # scripts are validated as much as possible before being run. Afterwards, the
  # scripts are run. If an error occurs, the entire experiment is halted.
  def start(self):

    # Print out all machine addresses used. This will allow us to better
    # collect the data later.
    machines_file = open(os.path.join(self.get_expdir(), "MACHINE_LIST"), 'w')
    for machine in self.get_machines():
      ipaddr = machine.get_ipaddr()
      if machine.isLocal:
        print >> machines_file, "LOCAL: %s" % (ipaddr)
      else:
        print >> machines_file, "REMOTE: %s" % (ipaddr)
    machines_file.close()

    # Run all of the scripts in order. Each time we run scripts, we need to
    # make sure permissions on the folder are up to date in case something was
    # created by a previous step.

    self.parse_wf_step(self.INIT_ENV)

    for xcn_node in self.get_all_nodes():
      xcn_node.parse_wf_step(self.INIT_NODE)

    self.parse_wf_step(self.START_ENV)

    for xcn_node in self.get_all_nodes():
      xcn_node.parse_wf_step(self.START_NODE)

    for xcn_node in self.get_all_nodes():
      xcn_node.parse_wf_step(self.STOP_NODE)

    self.parse_wf_step(self.STOP_ENV)

    # Run scripts to initialize the environment
    xcn_utils.recursive_chown(self.get_expdir(), USER_UID, USER_GID)

    for machine in self.get_machines():
      machine.gen_init_script()
      machine.gen_start_script()
      machine.gen_stop_script()

    for machine in self.get_machines():
      if not machine.isLocal:
        print "Copying xcn directory to %s" % (machine.ipaddr)
        xcn_utils.scp_recursive(machine.ipaddr, self.get_expdir())

    print

    # Run scripts to initialize each node. These will all be done in parallel
    # and we will call p.wait to ensure we don't continue until all scripts
    # have finished.
    procs = []
    for machine in self.get_machines():
      p = machine.execute_init_script()
      procs.append(p)

    self.wait_for_procs(procs)
 
    # Sleep to allow environment or nodes additional time to setup.
    if self.get_init_time() > 0:
      init_time = self.get_init_time()
      print("Initialized all Nodes, sleeping for %d seconds" % init_time)
      time.sleep(init_time)

    # Run the scripts to start the experiment/test environment
    procs = []
    for machine in self.get_machines():
      p = machine.execute_start_script()
      procs.append(p)

    self.wait_for_procs(procs)

    # If duration is set, then we'll start a countdown. Otherwise, we'll run a
    # counter and continue running until all of the above scripts have finished.
    if self.get_duration() > 0:
      duration = self.get_duration()
      print("Scenario Started, running for %d seconds" % duration)
      while duration > 0:
        print duration
        time.sleep(min(5, duration))
        duration -= 5

    # Run the scripts to stop each node. All of these scripts will be run in
    # parallel and we will call p.wait to ensure we don't continue until all
    # scripts have finished.
    procs = []
    for machine in self.get_machines():
      p = machine.execute_stop_script()
      procs.append(p)

    self.wait_for_procs(procs)

  def parse_wf_step(self, wf_step):
    for cmd in self.COMMANDS[wf_step]:
      for machine in self.get_machines():
        machine.parse_entry(wf_step, cmd)

    for machine in self.get_machines():
      script = machine.get_script(wf_step)
      script.flush()

  def add_module(self, obj):
    self.MODULES.add(obj)

    for wf_step in [self.INIT_ENV, self.START_ENV, self.STOP_ENV]:
      if wf_step in dir(obj):
        self.COMMANDS[wf_step].append(getattr(obj, wf_step))

    if self.INIT_NODE in dir(obj) or self.START_NODE in dir(
        obj) or self.STOP_NODE in dir(obj):
      for xcn_node in obj.get_nodes():
        xcn_node.add_module(obj)

  def add_cmd(self, wf_step, cmd):
    if self.COMMANDS.has_key(wf_step):
      self.COMMANDS[wf_step.lower().strip()].append(cmd)

    if wf_step in [self.INIT_NODE, self.START_NODE, self.STOP_NODE]:
      for xcn_node in self.get_all_nodes():
        xcn_node.add_cmd(wf_step, cmd)

    else:
      print "ERROR: Unknown workflow step: %s" % wf_step
      os._exit(1)

  def set_global(self, key, value):
    if type(key) is str:
      key = key.lower()
    self.__globals[key] = value

  def has_global(self, key):
    if type(key) is str:
      key = key.lower()
    return self.__globals.has_key(key)

  def get_global(self, key):
    if type(key) is str:
      key = key.lower()
    if not self.__globals.has_key(key):
      print "ERROR: Unable to get XCN_ENV key '%s'" % key
      os._exit(1)
    return self.__globals[key]

  def wait_for_procs(self, procs):
    for name, p in procs:
      ret = p.wait()
      if ret != 0:
        print "ERROR running %s" % name
        os._exit(ret)


# Container class for host machines involved in the experiment. Each node will
# be assigned to a different machine using a round robin scheme.
class XCN_MACHINE:

  def __init__(self, xcn_env, machineid, ipaddr, isLocal=True):
    self.xcn_env = xcn_env
    self.machineid = machineid
    self.ipaddr = socket.gethostbyname(ipaddr)

    if self.ipaddr == "127.0.0.1":
      self.isLocal = True
      iface, ipaddr = xcn_utils.get_primary_iface()
      self.ipaddr = ipaddr
      xcn_env.set_primary_iface(iface)

    else:
      self.isLocal = xcn_utils.has_ipaddr(self.ipaddr)

    self.nodes = []

    # Create the env scripts
    self.__init_env_script = False
    self.__start_env_script = False
    self.__stop_env_script = False

    self.__vars = {}

  def get_machineid(self):
    return self.machineid

  def get_ipaddr(self):
    return self.ipaddr

  def add_node(self, xcn_node):
    self.nodes.append(xcn_node)

  def get_nodes(self):
    return self.nodes

  def get_run_script(self):
    return self.run_script

  def get_script(self, wf_step):
    wf_step = wf_step.lower().strip()

    if wf_step == self.xcn_env.INIT_ENV:
      if self.__init_env_script is False:
        self.__init_env_script = XCN_SCRIPT(self.xcn_env, ".", "%s%d" % (self.xcn_env.INIT_ENV, self.machineid))
      return self.__init_env_script
    elif wf_step == self.xcn_env.START_ENV:
      if self.__start_env_script is False:
        self.__start_env_script = XCN_SCRIPT(self.xcn_env, ".", "%s%d" % (self.xcn_env.START_ENV, self.machineid))
      return self.__start_env_script
    elif wf_step == self.xcn_env.STOP_ENV:
      if self.__stop_env_script is False:
        self.__stop_env_script = XCN_SCRIPT(self.xcn_env, ".", "%s%d" % (self.xcn_env.STOP_ENV, self.machineid))
      return self.__stop_env_script
    else:
      print "ERROR: Unknown ENV workflow step: %s" % wf_step
      os._exit(1)

  # Helper function for parsing entries in the __*_env_scripts
  def parse_entry(self, wf_step, entry):
    script = self.get_script(wf_step)

    if type(entry) is str:
      entry = entry.replace("{{RUNID}}", self.xcn_env.get_runid())
      entry = entry.replace("{{NUMNODES}}", self.xcn_env.get_num_nodes())
      entry = entry.replace("{{EXPDIR}}", self.xcn_env.get_expdir())
      entry = entry.replace("{{LOGDIR}}", self.xcn_env.get_logdir())
      entry = entry.replace("{{VARDIR}}", self.xcn_env.get_vardir())
      script.append_run_cmd(entry)
    elif hasattr(entry, '__call__') or hasattr(entry, '__init__'):
      entry(self, script)
    else:
      print "ERROR: Commands must be either strings or function calls"
      print entry
      os._exit(1)

  def gen_script(self, name, env_step, node_step, reverse_order=False):
    fullpath = os.path.join(self.xcn_env.get_expdir(), name)
    print "Generating %s" % fullpath

    script = xcn_utils.write_shell_script(fullpath)
    print >> script, 'cd $(dirname $0)'
    print >> script

    if not reverse_order:
      print >> script, "bash %s" % self.get_script(env_step).path

    for xcn_node in self.get_nodes():
      precmd = xcn_node.get_access_cmd()
      if precmd.startswith("ssh"):
        precmd = precmd.replace("ssh", "ssh -f", 1)
        print >> script, '%s "(cd `pwd` && bash %s)"' % (precmd, xcn_node.get_script(node_step).path)
      else:
        print >> script, "%s bash %s &" % (precmd, xcn_node.get_script(node_step).path)

    print >> script, "wait"
    if reverse_order:
      print >> script, "bash %s" % self.get_script(env_step).path
    print >> script
    print >> script, "exit 0"

  def execute_script(self, name):
    name = name.strip()

    # Always execute from the xcn_env.get_expdir() directory so all scripts can use
    # relative paths.
    if self.isLocal:
      cmd = "bash %s/%s" % (self.xcn_env.get_expdir(), name)
    else:
      cmd = "ssh %s (%s/%s) &> /dev/null" % (self.ipaddr, self.xcn_env.get_expdir(), name)

    print "RUNNING: %s" % cmd
    p = subprocess.Popen(cmd.split())

    return name, p

  def gen_init_script(self):
    self.gen_script("init%d.sh" % self.machineid, self.xcn_env.INIT_ENV, self.xcn_env.INIT_NODE)

  def gen_start_script(self):
    self.gen_script("start%d.sh" % self.machineid, self.xcn_env.START_ENV, self.xcn_env.START_NODE)

  def gen_stop_script(self):
    self.gen_script("stop%d.sh" % self.machineid, self.xcn_env.STOP_ENV, self.xcn_env.STOP_NODE, True)

  def execute_init_script(self):
    return self.execute_script("init%d.sh" % self.machineid)

  def execute_start_script(self):
    return self.execute_script("start%d.sh" % self.machineid)

  def execute_stop_script(self):
    return self.execute_script("stop%d.sh" % self.machineid)

  def set_var(self, key, value):
    if type(key) is str:
      key = key.lower()
    self.__vars[key] = value

  def has_var(self, key):
    if type(key) is str:
      key = key.lower()
    return self.__vars.has_key(key)

  def get_var(self, key):
    if type(key) is str:
      key = key.lower()
    assert self.__vars.has_key(key)
    return self.__vars[key]



# Container class for a node. This class will store all generic information
# about a node and also allow storing module specific information using a
# dictionary. This dictionary isn't used by any XCN_*. However, there is no
# guarantee that different modules cannot over write each other's entries, so
# care must be taken when specifying the key used for each entry.
class XCN_NODE:

  def __init__(self, parent, nodeid, nodename=False):
    self.parent = parent
    self.__ID = int(nodeid)

    if self.__ID <= 0:
      print "ERROR: Node IDs must be greater than 0"
      os._exit(1)

    if nodename:
      self.__NAME = nodename
    else:
      self.__NAME = "n%d" % (self.get_nodeid())

    self.__NAME = "%s-%d" % (self.__NAME, parent.get_runid())

    # create a var and logs directory for the node
    self.set_vardir(os.path.join(self.get_nodename(), "var"))
    var_path = os.path.join(parent.get_expdir(), self.get_vardir())
    if os.path.isdir(var_path):
      print "ERROR: Directory %s already exists" % var_path
      os._exit(1)
    os.makedirs(var_path)

    self.set_logdir(os.path.join(self.get_nodename(), "logs"))
    log_path = os.path.join(parent.get_expdir(), self.get_logdir())
    if os.path.isdir(log_path):
      print "ERROR: Directory %s already exists" % log_path
      os._exit(1)
    os.makedirs(log_path)

    # Scripts used for the workflow of each node
    self.__init_node_script = XCN_SCRIPT(parent, self.get_vardir(),
                                         parent.INIT_NODE)
    self.__start_node_script = XCN_SCRIPT(parent, self.get_vardir(),
                                          parent.START_NODE)
    self.__stop_node_script = XCN_SCRIPT(parent, self.get_vardir(),
                                         parent.STOP_NODE)

    # Variable to store a command to access this node (such as ssh or
    # lxc-attach)
    self.ACCESS_CMD = ""

    self.COMMANDS = {}
    self.COMMANDS[self.parent.INIT_NODE] = []
    self.COMMANDS[self.parent.START_NODE] = []
    self.COMMANDS[self.parent.STOP_NODE] = []

    # Private dictionary for node specific variables, should be only accessed
    # with the getter/setter functions.
    self.__vars = {}

    self.__machine = False

  def get_nodeid(self):
    return self.__ID

  def get_nodename(self):
    return self.__NAME

  def set_nodedir(self, value):
    self.NODEDIR = value

  def get_nodedir(self):
    return self.NODEDIR

  def set_vardir(self, value):
    self.__VARDIR = value

  def get_vardir(self):
    return self.__VARDIR

  def set_logdir(self, value):
    self.__LOGDIR = value

  def get_logdir(self):
    return self.__LOGDIR

  def add_machine(self, machine):
    self.__machine = machine

  def get_machine(self):
    return self.__machine

  def get_script(self, wf_step):
    wf_step = wf_step.lower().strip()

    if wf_step == self.parent.INIT_NODE:
      return self.__init_node_script
    elif wf_step == self.parent.START_NODE:
      return self.__start_node_script
    elif wf_step == self.parent.STOP_NODE:
      return self.__stop_node_script
    else:
      print "ERROR: Unknown NODE workflow step: %s" % wf_step
      os._exit(1)

  def replace_tokens(self, entry):
    if type(entry) is not str:
      print "ERROR: Unable to parse entry: ", entry
      sys.exit(1)

    entry = entry.replace("{{RUNID}}", str(self.parent.get_runid()))
    entry = entry.replace("{{NODENAME}}", self.get_nodename())
    entry = entry.replace("{{NODEID}}", str(self.get_nodeid()))
    entry = entry.replace("{{LOGDIR}}", self.get_logdir())
    entry = entry.replace("{{VARDIR}}", self.get_vardir())
    return entry

# Helper function for parsing entries in the __*_node_scripts

  def parse_node_entry(self, script, entry):
    etype = type(entry)

    if hasattr(entry, '__call__') or hasattr(entry, '__module__'):
      entry(self, script)
    elif etype is list or etype is tuple:
      if len(entry) != 3:
        print "Tuple entries must be of the format (time_in_ms, xcn_node, cmd)"
        return
      t, nodeid, entry = entry
      if nodeid != self.get_nodeid():
        return
      entry = self.replace_tokens(entry)
      script.append_run_cmd(script.mk_group([script.mk_sleep(t), entry]))

    # We need to replace {{NAME}} with self.get_nodename() and {{ID}} with self.get_nodeid().
    elif etype is str:
      entry = self.replace_tokens(entry)
      script.append_run_cmd(entry)

    else:
      print "ERROR: Commands must be either strings or function calls"
      print entry
      os._exit(1)

  def parse_wf_step(self, wf_step):
    script = self.get_script(wf_step)

    for cmd in self.COMMANDS[wf_step]:
      self.parse_node_entry(script, cmd)

    script.flush()

  # The purpose of this funciton is to add a module to a specific node (rather
  # than all nodes as is done when using xcn_env.add_module)
  def add_module(self, obj):
    self.parent.MODULES.add(obj)

    for wf_step in [self.parent.INIT_NODE, self.parent.START_NODE, self.parent.STOP_NODE]:
      if wf_step in dir(obj):
        self.COMMANDS[wf_step].append(getattr(obj, wf_step))

  # The purpose of this funciton is to add a module to a specific node (rather
  # than all nodes as is done when using parent.add_cmd)
  def add_cmd(self, wf_step, cmd):
    if self.COMMANDS.has_key(wf_step):
      self.COMMANDS[wf_step.lower().strip()].append(cmd)

  def set_access_cmd(self, access_cmd):
    print "Node %d access command: %s" % (self.get_nodeid(), access_cmd)
    self.ACCESS_CMD = access_cmd

  def get_access_cmd(self):
    return self.ACCESS_CMD

  def set_var(self, key, value):
    if type(key) is str:
      key = key.lower()
    self.__vars[key] = value

  def has_var(self, key):
    if type(key) is str:
      key = key.lower()
    return self.__vars.has_key(key)

  def get_var(self, key):
    if type(key) is str:
      key = key.lower()
    assert self.__vars.has_key(key)
    return self.__vars[key]


# Container for writing commands to a bash script.
class XCN_SCRIPT:

  def __init__(self, xcn_env, rundir, name):
    self.name = "%s.sh" % name
    self.xcn_env = xcn_env
    self.rundir = rundir

    basedir = os.path.join(xcn_env.get_expdir(), rundir)
    if not os.path.isdir(basedir):
      print "ERROR: Unable to find directory %s" % self.rundir
      os._exit(1)

    self.path = os.path.join(self.rundir, self.name)
    fullpath = os.path.join(xcn_env.get_expdir(), self.path)
    if os.path.isfile(fullpath):
      print "ERROR: %s already exists, cannot overwrite" % fullpath
      os._exit(1)

    self.script = xcn_utils.write_shell_script(fullpath)

    self.run_cmds = []
    self.validate_cmds = []

  def add_os_dependency(value):
    print "IMPLEMENT ME"
    sys.exit(1)

  def append_run_cmd(self, cmd, bg=False, devnull=False):
    if type(cmd) is not str:
      print "ERROR: Received non-string command"
      os._exit(1)

    if bg:
      cmd += " &"

    if devnull:
      cmd += " &> /dev/null"

    self.run_cmds.append(cmd)

  def append_validate_cmd(self, cmd, bg=False, devnull=False):
    if type(cmd) is not str:
      print "ERROR: Received non-string command"
      os._exit(1)

    if bg:
      cmd += " &"

    if devnull:
      cmd += " &> /dev/null"

    self.validate_cmds.append(cmd)

  def mk_print(self, string, nl=True, bg=False):
    if string.startswith("-"):
      print "ERROR: Print strings must not start with '-': %s" % string
      os._exit(1)

    if nl:
      string = "echo %s" % string
    else:
      string = "echo -n %s" % string
    if bg:
      string += " &"

    return string

  def mk_sleep(self, value):
    value = value / 1000.0
    return "sleep %f" % value

  def mk_group(self, cmds, bg=False):
    cmds = " && ".join(cmds)
    if bg:
      cmds = "(%s) &" % (cmds)

    return cmds

  def mk_redirect_to_file(self, cmd, file_name, append=False, bg=False):
    if append:
      cmd += " &>> %s" % file_name
    else:
      cmd += " &> %s" % file_name

    if bg:
      cmd = "%s &" % (cmd)

    return cmd

  def mk_check_proc(self, process_name, exit_status=1):
    return "ps aux |grep -v grep |grep -q -o %s || exit %d" % (process_name,
                                                               exit_status)

  def mk_wait_proc(self,
                   process_name,
                   sleep_time=1000,
                   max_loops=False,
                   exit_status=1):
    sleep_time = sleep_time / 1000.0
    cmd = "while (! ps aux |grep -v grep |grep -q -o %s); do sleep %f" % (
        process_name, sleep_time)

    if max_loops:
      cmd = "count=0; %s" % cmd
      cmd += "; [ $count -eq %d ] && exit %d; ((count++))" % (max_loops,
                                                              exit_status)

    cmd += "; done"
    return cmd

  def mk_check_interface(self, interface_name, exit_status=1):
    return "ip link show |grep -q -o %s || exit %d" % (interface_name,
                                                       exit_status)

  def mk_wait_interface(self,
                        interface_name,
                        sleep_time=1000,
                        max_loops=False,
                        exit_status=1):
    sleep_time = sleep_time / 1000.0
    cmd = "while (! ip link show |grep -q -o %s); do sleep %f" % (
        interface_name, sleep_time)

    if max_loops:
      cmd = "count=0; %s" % cmd
      cmd += "; [ $count -eq %d ] && exit %d; ((count++))" % (max_loops,
                                                              exit_status)

    cmd += "; done"
    return cmd

  def mk_check_file(self, file_name, exit_status=1):
    return "test -f %s || exit %d" % (file_name, exit_status)

  def mk_wait_file(self,
                   file_name,
                   sleep_time=1000,
                   max_loops=False,
                   exit_status=1):
    sleep_time = sleep_time / 1000.0
    cmd = "while (! test -f %s); do sleep %f" % (file_name, sleep_time)

    if max_loops:
      cmd = "count=0; %s" % cmd
      cmd += "; [ $count -eq %d ] && exit %d; ((count++))" % (max_loops,
                                                              exit_status)

    cmd += "; done"
    return cmd

  # Dumps all commands into a script, dumping the run_cmds first and then the
  # validate_cmds.
  def flush(self):
    for cmd in self.run_cmds:
      print >> self.script, cmd

    for cmd in self.validate_cmds:
      print >> self.script, cmd

    # We must have the script exit with a 0 return code so we can properly
    # detect non-zero return codes from the script.
    print >> self.script, "exit 0"
    self.script.close()

    self.run_cmds = []
    self.validate_cmds = []
