#!/bin/bash

HOSTNAME=$(hostname)
SERVER="mreich-asuslaptop-q540vj"

if [ "$HOSTNAME" = "mreich-nano1" ]; then
    SOUNDCARD="left_only"
elif [ "$HOSTNAME" = "mreich-nano2" ]; then
    SOUNDCARD="right_only"
else
    echo "Unknown hostname: $HOSTNAME"
    exit 1
fi

echo "Starting snapclient on $HOSTNAME with soundcard: $SOUNDCARD"
snapclient -h "$SERVER" --soundcard "$SOUNDCARD"