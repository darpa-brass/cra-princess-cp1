#!/usr/bin/env bash

# Configure system for Java
export JAVA_HOME=/usr/java/jdk1.8.0_211
export PATH=$PATH:$JAVA_HOME/bin
update-alternatives --install "/usr/bin/java" "java" "/usr/java/jdk1.8.0_211/bin/java" 1
update-alternatives --install "/usr/bin/javac" "javac" "/usr/java/jdk1.8.0_211/bin/javac" 1
update-alternatives --install "/usr/bin/javaws" "javaws" "/usr/java/jdk1.8.0_211/bin/javaws" 1
update-alternatives --set java /usr/java/jdk1.8.0_211/bin/java
update-alternatives --set javac /usr/java/jdk1.8.0_211/bin/javac
update-alternatives --set javaws /usr/java/jdk1.8.0_211/bin/javaws

# Upgrade the package installer
apt-get -y upgrade

# Update package manager
apt-get update

# Common Packages
apt-get install -y build-essential tcl tk --no-install-recommends
apt-get install -y libpq-dev vim --no-install-recommends
apt-get install -y software-properties-common --no-install-recommends
apt-get install -f -y

# Scala 2.12.3
wget www.scala-lang.org/files/archive/scala-2.12.3.deb
dpkg -i scala-2.12.3.deb

# SBT 0.13.15
wget -c https://bintray.com/artifact/download/sbt/debian/sbt-0.13.15.deb
dpkg -i sbt-0.13.15.deb
apt-get update
apt-get install sbt
apt-get install -f -y

# jq
apt-get install -y jq
apt-get update
apt-get install -f -y

# Octave & GNUPlot
add-apt-repository -y ppa:octave/stable
apt-get update
apt-get -y install octave liboctave-dev gnuplot --no-install-recommends
apt-get install -f -y

# Apache ActiveMQ 5.14.0
wget https://archive.apache.org/dist/activemq/5.14.0/apache-activemq-5.14.0-bin.tar.gz
tar -C /cp3 -zxvf apache-activemq-5.14.0-bin.tar.gz

# Python Packages
apt-add-repository universe
apt-get update
apt-get install -y python3-software-properties --no-install-recommends
apt-get install -y python3-dev --no-install-recommends
apt-get install -y python3-pip --no-install-recommends
apt-get install -y python3-setuptools --no-install-recommends

pip3 install numpy
pip3 install scipy
pip3 install scikit-learn
pip3 install pyorient
pip3 install lxml
pip3 install ortools
pip3 install pandas
pip3 install matplotlib

# Cleanup Install Artifacts
rm -f scala-2.12.2.deb
rm -f sbt-0.13.15.deb
rm -f apache-activemq-5.14.0-bin.tar.gz

# Clean up previous logs / scenarios
rm -f princess.log
rm -f scenario.json
