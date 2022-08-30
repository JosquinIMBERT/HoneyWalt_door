#!/bin/bash

if [[ $# -ne 1 ]]; then
	exit 1
fi

path=$1

umask 077;
wg genkey >${path}privkey;
wg pubkey <${path}privkey >${path}pubkey;
cat privkey pubkey