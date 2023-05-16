#!/bin/bash

# Installing dependencies
apt update
apt install wireguard python3-pip iptables
pip3 install python_wireguard

# Adding environment variable
dir=$(dirname $0)
home=$(realpath ${dir}/../)
if [ ! -f ~/.bash_profile ] || ! grep -q HONEYWALT_DOOR_HOME <~/.bash_profile; then
        echo "export HONEYWALT_DOOR_HOME=${home}/" >> ~/.bash_profile
fi

# Include ~/.bash_profile if ~/.bashrc does not exist or if it does not include it already
if [ ! -f ~/.bashrc ] || ! grep -q \.bash_profile <~/.bashrc; then
cat <<EOT >> ~/.bashrc
if [ -f ~/.bash_profile ]; then
    . ~/.bash_profile
fi
EOT
fi
