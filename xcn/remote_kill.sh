#/bin/bash

curdir=$(cd `dirname $0` && pwd)
script="kill.sh"

host=$1
shift

ssh $host "cd $curdir && svn up && ./$script $*"
