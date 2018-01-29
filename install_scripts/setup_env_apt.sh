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

apt-get install -y \
  software-properties-common \
  python-software-properties

apt-get update
apt-get install -y \
  acpid \
  ant \
  autoconf \
  automake \
  bison \
  bridge-utils \
  bzr \
  cmake \
  curl \
  cython \
  doxygen \
  flex \
  g++ \
  gcc \
  gdb \
  git \
  gsl-bin \
  iperf \
  iproute \
  javacc \
  javacc-doc \
  java-common \
  libace-dev \
  libboost-all-dev \
  libcurl3 \
  libcurl4-openssl-dev \
  libev-dev \
  libgoocanvas-dev \
  libgsl-dev \
  libgtk2.0-0 \
  libgtk2.0-dev \
  libjson0 \
  libjson0-dev \
  libpcap-dev \
  libpcre3-dev \
  libssl-dev \
  libtool \
  libxml2 \
  libxml2-dev \
  libxml-libxml-perl \
  libxml-namespacesupport-perl \
  libxml-sax-base-perl \
  libxml-sax-perl \
  libxml-simple-perl \
  make \
  maven \
  mercurial \
  nfs-common \
  openjdk-[78]* \
  openssh-client \
  openssh-server \
  psmisc \
  python \
  python-setuptools \
  python-dev \
  tcl-dev \
  tcpdump \
  tk-dev \
  unzip \
  uuid-dev \
  valgrind \
  vim \
  zip

sudo easy_install pip
pip install lxml \
            matplotlib \
            pyelasticsearch \
            flask \
            bottle \
            elasticsearch-dsl \
            networkx \
            netifaces \
            numpy \
            scipy

#
# Setup VIM as default editor
#
vim_basic=`update-alternatives --list editor |grep -m 1 vim.basic`
update-alternatives --set editor $vim_basic

apt-get -y clean
apt-get -y autoclean
apt-get -y autoremove --purge
