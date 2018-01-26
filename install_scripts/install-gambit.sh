#! /bin/bash

sudo apt-get install cython
sudo pip install nose

# include the utils.sh script
source ./setup-utils.sh

#download_file https://downloads.sourceforge.net/project/gambit/gambit15/15.1.0/gambit-15.1.0.tar.gz
download_file https://downloads.sourceforge.net/project/gambit/gambit16/16.0.0/gambit-16.0.0.tar.gz
install_typical

cd $INSTALL_DIR
cd src/python
python setup.py build || exit 1
python setup.py install || exit 1
