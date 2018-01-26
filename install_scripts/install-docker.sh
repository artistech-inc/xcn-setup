#!/bin/bash

source ./setup-utils.sh

UBUNTU_RELEASE=`lsb_release -cs`
if [ "$UBUNTU_RELEASE" != "trusty" -a "$UBUNTU_RELEASE" != "xenial" ]; then
  echo "Unable to install docker"
  exit 1
fi

apt-get update
apt-get install -y apt-transport-https ca-certificates
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D

echo "deb https://apt.dockerproject.org/repo ubuntu-$UBUNTU_RELEASE main" > docker.list
mv docker.list /etc/apt/sources.list.d/
apt-get update

apt-cache policy docker-engine
apt-get install -y linux-image-extra-$(uname -r) linux-image-extra-virtual
apt-get install -y docker-engine
service docker start

usermod -aG docker $SUDO_USER
docker pull ubuntu:$(lsb_release -cs)

echo
echo "****************************************************************"
echo "Restart your shell to run docker without needing sudo privileges"
echo "****************************************************************"
echo
