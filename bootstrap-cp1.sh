#!/usr/bin/env bash

# Upgrade the package installer
apt-get -y upgrade

# Update package manager
apt-get update

# Common Packages
apt-get install -y build-essential tcl tk --no-install-recommends
apt-get install -y libpq-dev vim --no-install-recommends
apt-get install -y software-properties-common python-software-properties

# Python 3.6 and packages
apt-get -y install software-properties-common --no-install-recommends
apt-add-repository universe
apt-get update
apt-get -y install python3.6 --no-install-recommends
apt-get -y install python-dev --no-install-recommends
apt-get -y install python-pip --no-install-recommends
apt-get -y install python-setuptools --no-install-recommends
pip install --upgrade pip
pip install pyorient
pip install lxml

# Access Control Settings
chmod 777 ./start
