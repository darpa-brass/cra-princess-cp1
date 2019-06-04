#!/usr/bin/env bash

# Upgrade the package installer
apt-get -y upgrade

# Update package manager
apt-get update

# Common Packages
apt-get install -y build-essential tcl tk --no-install-recommends
apt-get install -y libpq-dev vim --no-install-recommends
apt-get install -y software-properties-common python3-software-properties --no-install-recommends

# Python 3.6 and packages
apt-add-repository universe
apt-get update
# apt-get -y install python3.6 --no-install-recommends
apt-get -y install python3-dev --no-install-recommends
apt-get -y install python3-pip --no-install-recommends
apt-get -y install python3-setuptools --no-install-recommends
# pip3 install --upgrade pip

pip3 install numpy
pip3 install scipy
pip3 install scikit-learn
pip3 install pyorient
pip3 install lxml
pip3 install ortools
