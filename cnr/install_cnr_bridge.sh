#!/bin/bash

# Check if the source is checked out
if [[ ! -f Vbs3EmanePlugin/target/cnr-bridge-1.0.jar ]];
then
    # checkout the source
    echo "git clone https://github.com/artistech-inc/Vbs3EmanePlugin.git"
    git clone https://github.com/artistech-inc/Vbs3EmanePlugin.git

    # grab the latest source
    cd Vbs3EmanePlugin
    git pull
    git checkout v1.0

    # build the latest source
    echo "mvn package"
    mvn package
fi
