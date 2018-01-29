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

dpkg --list |grep "^iU.*linux-image" 2>&1 > /dev/null
if [ $? -eq 1 ]; then
  echo "Found uninstalled update. If this script fails, try removing it and re-running this script again after:"
  dpkg --list |grep "^iU.*linux-image" | awk '{print $2}' |xargs echo "  dpkg -r"
fi

BOOT_USE=`df |grep boot|awk '{print $5}' |sed -e 's/%//'`
if [ $BOOT_USE -gt 80 ]; then
  dpkg --list |grep "^i[iU].*linux-image"

  echo "/boot is at ${BOOT_USE}% full, you need to remove older images by using:"
  echo "  dpkg -r <image name>"

  l=`dpkg --list |grep "^i[iU].*linux-image" |wc -l`
  l=`expr $l - 4`
  dpkg --list |grep "^i[iU].*linux-image" |head -n $l | awk '{print $2}' |xargs echo "  dpkg -r"
  exit 1
fi

apt-get -f install

if [ $? -ne 0 ]; then
  echo "If an error occurred for a linux image, uninstall it using \"dpkg -r\" and re-run this script"
  exit 1
fi

apt-get autoremove
apt-get autoclean
apt-get clean
apt-get upgrade
