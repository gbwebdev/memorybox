#!/bin/bash

set -e

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Please run this script using sudo and/or as root"
  exit 1
fi

function run_as_user {
  if [ ! -z $SUDO_USER ]; then
    su $SUDO_USER -c "$1"
  else
    eval "$1"
  fi
}

echo "o Installing dependencies..."
apt update
apt install -y python3-venv git build-essential python3-dev sqlite3
apt install -y libbluetooth-dev
apt install -y libopenjp2-7 libtiff5-dev libtiff6
echo "  ...done."

if [ ! -d ./venv ]; then
  echo "o Creating python virtual environment..."
  run_as_user "python3 -m venv venv"
  echo "  ...done."
fi

echo "o Activating python virtual environment."
run_as_user "source venv/bin/activate"

echo "o Creating instance directory..."
mkdir -p /var/www/memorybox
if [ ! -z $SUDO_UID ]; then
  chown $SUDO_UID /var/www/memorybox
fi
echo "  ...done."

echo "o Installing memorybox python package..."
run_as_user "source venv/bin/activate && pip install ./pymemorybox"
echo "  ...done."

echo "> Installation complete !"
