#!/bin/bash

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Please run this script using sudo and/or as root"
  exit 1
fi

python3 -m venv venv
source venv/bin/activate

apt install -y libbluetooth-dev libopenjp2-7 libtiff5-dev libtiff6
pip install git+https://github.com/pybluez/pybluez@master#egg=pybluez

pip install peripage
