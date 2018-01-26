#! /bin/bash

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
