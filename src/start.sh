#!/bin/bash

# Usage: start.sh <log-level> [pidfile]

HOME=$(realpath $(dirname $(dirname "$0")))

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <log-level> [pidfile]"
	exit 1
else
	loglevel="$1"
fi

if [[ $# -gt 1 ]]; then
	pidfile="$1"
else
	pidfile="${HOME}/var/honeywalt_door.pid"
fi

# Start HoneyWalt_door
python ${HOME}/src/honeywalt_door.py \
	--log-level ${loglevel} \
	--pid-file ${pidfile}