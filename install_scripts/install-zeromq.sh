#! /bin/bash

# include the utils.sh script
source ./setup-utils.sh

ZEROMQ_VERSION=4.2.0

# Install ZeroMQ
download_file https://github.com/zeromq/libzmq/releases/download/v${ZEROMQ_VERSION}/zeromq-${ZEROMQ_VERSION}.tar.gz
install_typical

# C++ bindings
git_clone https://github.com/zeromq/cppzmq
(cd $INSTALL_DIR && sudo cp -r ../cppzmq /usr/include/)

# Python bindings
pip install --upgrade --use-wheel pyzmq || pip install --upgrade pyzmq

# Java bindings
git_clone https://github.com/zeromq/jzmq
export INSTALL_DIR=${INSTALL_DIR}/jzmq-jni
install_typical
