#!/bin/bash
# python and pip3
apt-get -y install python3 python3-pip
# python dependency packages
pip3 install -r requirements.txt
# pyre dependency package from github
pip3 install https://github.com/zeromq/pyre/archive/master.zip
