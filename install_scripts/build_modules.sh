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

CURDIR=`pwd`

# Shim
cd $CURDIR/../../Tools/core-shim/ || exit 1
rm -f core-shim.jar
ant || exit 1
ant -f package.xml || exit 1

# Shim CPP bindings
cd bindings/cpp || exit 1
./install-deps.sh  || exit 1
make || exit 1

# Algolink
cd $CURDIR/../algolink/ || exit 1
./build.sh || exit 1

# Elicit
$CURDIR/ubuntu_switch_java.sh 7
cd $CURDIR/../../Tools/elicit/ || exit 1
./setup.sh || exit 1

# Caching
cd $CURDIR/../../Tools/multi-genre-caching/ || exit 1
make

# ZeroMQ multicast tunnel app
cd $CURDIR/../../Tools/zmq_mcast_tunnel/ || exit 1
make

