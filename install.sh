#!/bin/bash

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Please run this script using sudo and/or as root"
  exit 1
fi

function run_as_user {
  if [ ! -z $SUDO_USER ]; then
    su - $SUDO_USER -c "$1"
  else
    eval "$1"
  fi
}

if [ ! -d ./venv ]; then
  run_as_user "python3 -m venv venv"
fi

run_as_user "source venv/bin/activate"

apt install -y libbluetooth-dev
apt install -y libopenjp2-7 libtiff5-dev libtiff6

mkdir -p /var/www/memorybox
if [ ! -z $SUDO_UID ]; then
  chown $SUDO_UID /var/www/memorybox
  run_as_user "source venv/bin/activate && pip install ./memorybox"
fi
