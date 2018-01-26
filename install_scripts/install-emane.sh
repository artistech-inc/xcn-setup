#! /bin/bash

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
