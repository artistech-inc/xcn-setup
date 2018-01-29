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

if [ -z "$1" ]; then
  echo "usage(): $0 (6|7|8)"
  exit 1
fi

if [ $1 -lt 6 -o $1 -gt 8 ]; then
  echo "usage(): $0 (6|7|8)"
  exit 1
fi

set_java() {
  dir=`sudo update-alternatives --list $1 |grep java-$2`

  if [ $? -ne 0 ]; then
    echo "Unable to find specified version of java: $2"
    exit 1
  fi

  sudo update-alternatives --set $1 $dir
}

set_java java $1
set_java javac $1
set_java jar $1
set_java javadoc $1
set_java jarsigner $1
set_java keytool $1

export JAVA_HOME=`ls -1 -d /usr/lib/jvm/java-${1}*`
echo "export JAVA_HOME=${JAVA_HOME}"
