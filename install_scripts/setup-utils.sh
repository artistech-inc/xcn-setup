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

if [ $EUID -ne 0 ]; then
  exec sudo "$0" "$@"
fi

# make sure we're in the directory this script exists
cd `dirname $0`

test_for_binary() {
  which $1 &> /dev/null
  echo $?
}

git_clone() {
  export CUR_DIR=`pwd`

  # setup download directory for pushing downloaded files
  mkdir -p cached
  cd cached

  export DOWNLOADED=`basename $1 '.git'`
  [ ! -d "$DOWNLOADED" ] && git clone $1

  if [ ! -d "$DOWNLOADED" ]; then
    echo "Error cloning git repo: $1"
    cd $CUR_DIR
    return 1
  fi

  cd $DOWNLOADED
  export INSTALL_DIR=`pwd`

  if [ ! -z "$2" ]; then
    git checkout $2
  fi

  cd $CUR_DIR

  return 0
}

download_file() {
  # setup download directory for pushing downloaded files
  mkdir -p cached

  export DOWNLOADED=`pwd`/cached/`basename $1`
  [ -f "$DOWNLOADED" ] && return 0

  # try wget
  if [ `test_for_binary wget` -eq 0 ]; then
    wget -P cached $1

  # try curl
  elif [ `test_for_binary curl` -eq 0 ]; then
    curl -L -o $DOWNLOADED $1

  fi

  [ -f "$DOWNLOADED" ] && return 0

  echo "Either wget or curl are not installed or $1 could not be downloaded, exiting..."
  exit 1
}

extract_download() {
  export CUR_DIR=`pwd`
  cd cached

  t=`file --mime-type $DOWNLOADED |awk '{print $2}' |awk -F '/' '{print $2}' |sed -e 's/x-//'`
  if [ "$t" = "gzip" ]; then
    INSTALL_DIR=`tar tvfz $DOWNLOADED |head -n 1 |awk '{print $NF}'`
    tar xvfz $DOWNLOADED

  elif [ "$t" = "zip" ]; then
    INSTALL_DIR=`unzip -l $DOWNLOADED |awk '{print $4}' |grep '/' |awk -F '/' '{print $1}'|uniq`
    unzip -o $DOWNLOADED

  else
    echo "Unable to handle $DOWNLOADED in install_typical"
    cd $CUR_DIR
    return 1
  fi

  cd $INSTALL_DIR
  export INSTALL_DIR=`pwd`
  cd $CUR_DIR
}

install_typical() {
  export CUR_DIR=`pwd`

  if [ "$1" = "-ne" ]; then
    shift
  else
    extract_download
  fi
  cd $INSTALL_DIR

  AUTOGEN_ARGS=
  CONFIGURE_ARGS=

  # go through the command line arguments
  while [[ $# > 1 ]]; do
    key="$1"

    case $key in
      --autogen)
        AUTOGEN_ARGS="$2"
        shift
        ;;
      --configure)
        CONFIGURE_ARGS="$2"
        shift
        ;;
      *)
        echo "Invalid option: $key"
        exit 1
        ;;
    esac
    shift
  done

  [ ! -f "configure" -a -f "autogen.sh" ] && ./autogen.sh $AUTOGEN_ARGS

  if [ -f "configure" ]; then
    ./configure --prefix=/usr $CONFIGURE_ARGS
    if [ $? -ne 0 ]; then
      echo "ERROR Configuring $DOWNLOADED, exiting"
      exit 1
    fi
  fi

  NUM_PROC=`grep -m 1 'cpu cores' /proc/cpuinfo |awk '{print $NF}'`
  make -j $NUM_PROC && make install
  if [ $? -ne 0 ]; then
    echo "ERROR Building $DOWNLOADED, exiting"
    exit 1
  fi

  [ `test_for_binary ldconfig` -eq 0 ] && ldconfig 

  cd $CUR_DIR
  return 0
}
