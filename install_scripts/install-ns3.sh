#! /bin/bash

source ./setup-utils.sh

NS3_VERSION="3.24.1"

wget https://www.nsnam.org/release/ns-allinone-${NS3_VERSION}.tar.bz2
if [ $? -ne 0 ]; then
  echo "Unable to download NS3"
  exit 1
fi

bunzip2 ns-allinone-${NS3_VERSION}.tar.bz2 
tar xvf ns-allinone-${NS3_VERSION}.tar 

# download and build
cd ns-allinone-$NS3_VERSION
./build.py

# now link xcn files
ln -s `(cd ../../xcn && pwd)` ns-$NS3_VERSION/xcn

# now build ns3
cd ns-$NS3_VERSION
./waf --enable-sudo --enable-examples configure
./waf

cd ../..
