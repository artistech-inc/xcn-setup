#! /bin/bash
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

if [ -z "$1" -o ! -f "$1" ]; then
  echo "usage(): $0 <nodes.config>"
  exit 1
fi

CUR_DIR=$(cd `dirname $0` && pwd -P)

[ -z "${MGC_DIR}" ] && MGC_DIR=${CUR_DIR}/../../../Tools/multi-genre-caching/

MGC_DIR=`(cd $MGC_DIR && pwd -P)`
MGC_CONFIG=${MGC_DIR}/mgc.config
XCN_CONFIG=${MGC_DIR}/xcn.config

if [ ! -f "$MGC_CONFIG" ]; then
  echo "Unable to find $MGC_CONFIG, exiting"
  exit 1
fi

# Take the current default config and grep out non-commented configs
grep "^[A-Z]" $MGC_CONFIG > ${XCN_CONFIG}

# Convert this format:
#  0	n0	172.16.1.1/24	10.0.0.1/24
#
# To this:
#  MgcNI  NodeName        *       0 n0
while read line; do
  echo $line |awk '{print "MgcNI	NodeName	*	",$1,$2}' >> ${XCN_CONFIG}
done < $1
