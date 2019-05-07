#!/usr/bin/env bash

# Upgrade the package installer
sudo apt-get -y upgrade

# Update package manager
sudo apt-get update

# Common Packages
sudo apt-get install -y build-essential tcl tk --no-install-recommends
sudo apt-get install -y libpq-dev vim --no-install-recommends
sudo apt-get install -y software-properties-common python-software-properties
