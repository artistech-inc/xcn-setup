CURDIR=`pwd`

# Shim
cd $CURDIR/../../Tools/core-shim/ || exit 1
rm -f core-shim.jar
ant || exit 1
ant -f package.xml || exit 1

# Shim CPP bindings
cd bindings/cpp || exit 1
./install-deps.sh  || exit 1
make || exit 1

# Algolink
cd $CURDIR/../algolink/ || exit 1
./build.sh || exit 1

# Elicit
$CURDIR/ubuntu_switch_java.sh 7
cd $CURDIR/../../Tools/elicit/ || exit 1
./setup.sh || exit 1

# Caching
cd $CURDIR/../../Tools/multi-genre-caching/ || exit 1
make

# ZeroMQ multicast tunnel app
cd $CURDIR/../../Tools/zmq_mcast_tunnel/ || exit 1
make

