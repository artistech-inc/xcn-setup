#! /bin/bash

source ./setup-utils.sh

dpkg --list |grep "^iU.*linux-image" 2>&1 > /dev/null
if [ $? -eq 1 ]; then
  echo "Found uninstalled update. If this script fails, try removing it and re-running this script again after:"
  dpkg --list |grep "^iU.*linux-image" | awk '{print $2}' |xargs echo "  dpkg -r"
fi

BOOT_USE=`df |grep boot|awk '{print $5}' |sed -e 's/%//'`
if [ $BOOT_USE -gt 80 ]; then
  dpkg --list |grep "^i[iU].*linux-image"

  echo "/boot is at ${BOOT_USE}% full, you need to remove older images by using:"
  echo "  dpkg -r <image name>"

  l=`dpkg --list |grep "^i[iU].*linux-image" |wc -l`
  l=`expr $l - 4`
  dpkg --list |grep "^i[iU].*linux-image" |head -n $l | awk '{print $2}' |xargs echo "  dpkg -r"
  exit 1
fi

apt-get -f install

if [ $? -ne 0 ]; then
  echo "If an error occurred for a linux image, uninstall it using \"dpkg -r\" and re-run this script"
  exit 1
fi

apt-get autoremove
apt-get autoclean
apt-get clean
apt-get upgrade
