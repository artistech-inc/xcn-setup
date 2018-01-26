#! /bin/bash

if [ -z "$1" ]; then
  echo "usage(): $0 (6|7|8)"
  exit 1
fi

if [ $1 -lt 6 -o $1 -gt 8 ]; then
  echo "usage(): $0 (6|7|8)"
  exit 1
fi

set_java() {
  dir=`sudo update-alternatives --list $1 |grep java-$2`

  if [ $? -ne 0 ]; then
    echo "Unable to find specified version of java: $2"
    exit 1
  fi

  sudo update-alternatives --set $1 $dir
}

set_java java $1
set_java javac $1
set_java jar $1
set_java javadoc $1
set_java jarsigner $1
set_java keytool $1

export JAVA_HOME=`ls -1 -d /usr/lib/jvm/java-${1}*`
echo "export JAVA_HOME=${JAVA_HOME}"
