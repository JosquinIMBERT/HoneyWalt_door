#!/bin/bash

dir=$(realpath ${HONEYWALT_DOOR_HOME}/var/key/)

apt-get install -y easy-rsa
export PATH="$PATH:/usr/share/easy-rsa/"
export EASYRSA_BATCH=1

if [ ! -d "${dir}" ]; then
        echo "Error: HoneyWalt_door does not seem to be installed on this machine."
        exit 1
fi

role=server

cd ${dir}/
echo -n "Initializing client's PKI..." && easyrsa init-pki >/dev/null 2>&1 && echo "done" || echo "failed"
echo -n "Generating client cert request..." && easyrsa gen-req ${role} nopass >/dev/null 2>&1 && echo "done" || echo "failed"

echo
echo "Certificate request was successfully generated."
echo
echo "You can find it here: ${dir}/pki/reqs/${role}.req"
echo
echo "You should now copy it to the CA server, sign the request and copy back the resulting certificate to the '${dir}/pki/' directory with the name 'server.crt'."
echo
