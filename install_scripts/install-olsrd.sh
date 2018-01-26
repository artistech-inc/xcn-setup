#!/usr/bin/env bash

source ./setup-utils.sh

download_file http://www.olsr.org/releases/0.9/olsrd-0.9.0.3.tar.gz
extract_download

# Overwrite main.c, this removes using a lock file in /var. Without this
# change, we cannot run multiple OLSRD instances in different containers
# because they all attempt to use the same lock file.
cp files/olsrd/main.c $INSTALL_DIR/src/

install_typical -ne

cp files/olsrd/olsrd.conf /etc/olsrd/
