#!/usr/bin/env bash
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

source ./setup-utils.sh

# Version of EMANE to install
VERSION="1.0.1"

if [ -d cached/emane ]; then
  cd cached/emane
  make uninstall
  cd ../..
  rm -rf cached/emane
fi

which protoc &> /dev/null
if [ $? -eq 1 ]; then
  ./install-protobuf.sh || exit 1
fi

# test for Ubuntu
uname -a|grep -q Ubuntu
if [ $? -eq 0 ]; then

  apt-get install gcc g++ autoconf automake libtool libxml2-dev \
		  libpcap-dev libpcre3-dev \
		  uuid-dev debhelper pkg-config python-lxml python-setuptools \
                  git dh-python

  # Test if we have emane installed
  dpkg --list 2>&1 |grep emane > /dev/null
  if [ $? -eq 0 ]; then
    echo "EMANE is already installed on this machine, to remove, use the following command:"
    echo "  dpkg --remove \`dpkg --list |grep emane |awk '{print \$2}'\`"
    echo "or"
    echo "  cd cached/emane && make uninstall"
    exit 1
  fi

if [ $? -ne 0 ]; then
  echo "Error installing dependencies, please fix errors and run this script again"
  exit 1
fi


# CentOS 6 / Fedora
else
  yum install libxml2 pcre-devel uuid-devel python-lxml python-setuptools

  # Test if we have emane installed
  yum list 2>&1 |grep "emane"|awk '{print $1}' > /dev/null
  if [ $? -eq 0 ]; then
    echo "EMANE is already installed on this machine, to remove, use the following command:"
    echo "  yum erase \`yum list |grep "emane"|awk '{print \$1}'\`"
    exit 1
  fi

fi

# Download and install EMANE
git_clone https://github.com/adjacentlink/emane.git tags/v${VERSION}
install_typical -ne

cd $INSTALL_DIR/src/emanesh
python setup.py install
