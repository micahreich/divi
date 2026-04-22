#!/bin/bash

MONITOR="snapcast.monitor"
FIFO="/tmp/snapfifo"

# Create fifo if it doesn't exist
if [ ! -p "$FIFO" ]; then
    mkfifo "$FIFO"
fi

# Start snapserver
echo "Starting snapserver..."
sudo systemctl start snapserver

# Wait for it to be ready
sleep 2

# Start ffmpeg in background
echo "Starting audio capture from: $MONITOR"
echo "Play audio on this machine and it will stream to Snapcast clients"
echo "Press Ctrl+C to stop"

cleanup() {
    echo "Stopping..."
    sudo systemctl stop snapserver
    kill $FFMPEG_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

ffmpeg -f pulse -i snapcast.monitor -f s16le -ar 48000 -ac 2 /tmp/snapfifo

FFMPEG_PID=$!

wait $FFMPEG_PID