#!/bin/bash

HOSTS=("mreich@mreich-nano1.tail1e5887.ts.net" "mreich@mreich-nano2.tail1e5887.ts.net")
CMD="cd ~/divi && git git fetch && git pull"

for host in "${HOSTS[@]}"; do
    echo "--- $host ---"
    ssh "$host" "$CMD"
done