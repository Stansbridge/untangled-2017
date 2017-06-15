#!/bin/bash
# python and pip3
apt-get -y install python3 python3-pip
# python dependency packages by name
pip3 install bson pygame opensimplex
# pyre dependency package from github
pip3 install https://github.com/zeromq/pyre/archive/master.zip
