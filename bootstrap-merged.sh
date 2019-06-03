#!/usr/bin/env bash

# Upgrade the package installer
apt-get -y upgrade

# Update package manager
apt-get update

# Common Packages
apt-get install -y build-essential tcl tk --no-install-recommends
apt-get install -y libpq-dev vim --no-install-recommends
apt-get install -y software-properties-common python-software-properties --no-install-recommends

# Python 3.6 and packages
apt-add-repository universe
apt-get update
# apt-get -y install python3.6 --no-install-recommends
apt-get -y install python-dev --no-install-recommends
apt-get -y install python-pip --no-install-recommends
apt-get -y install python-setuptools --no-install-recommends
pip install --upgrade pip

pip install numpy
pip install scipy
pip install scikit-learn
pip install pyorient
pip install lxml
pip install ortools

# Brew and Octave
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"
# test -d ~/.linuxbrew && eval $(~/.linuxbrew/bin/brew shellenv)
# test -d /home/linuxbrew/.linuxbrew && eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)
# test -r ~/.bash_profile && echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.bash_profile
# echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.profile
# brew install octave

# Access Control Settings
chmod 777 ./start