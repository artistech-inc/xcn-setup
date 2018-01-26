#! /bin/bash

source ./setup-utils.sh

# Remove any preinstalled packages
dpkg --remove $(dpkg --list |grep -i protobuf |awk '{print $2}')

# Install protobuf version 2.6.1
GOOGLE_PROTOBUF_VERSION=2.6.1

download_file https://github.com/google/protobuf/releases/download/v${GOOGLE_PROTOBUF_VERSION}/protobuf-${GOOGLE_PROTOBUF_VERSION}.tar.gz
install_typical

# install the python bindings
(cd ${INSTALL_DIR}/python && python setup.py build && python setup.py install)

