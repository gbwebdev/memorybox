#!/bin/bash

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Please run this script using sudo and/or as root"
  exit 1
fi

if [ ! -z $SUDO_UID ]; then
  if [ ! -d ./venv ]; then
    su - $SUDO_UID -c "python3 -m venv venv"
  fi
  source venv/bin/activate
fi

apt install -y libbluetooth-dev
apt install -y libopenjp2-7 libtiff5-dev libtiff6

mkdir -p /var/www/memorybox
if [ ! -z $SUDO_UID ]; then
  chown $SUDO_UID /var/www/memorybox
  su - $SUDO_UID -c "source venv/bin/activate && pip install ./memorybox"
fi
