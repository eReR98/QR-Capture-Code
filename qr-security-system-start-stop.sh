#!/bin/sh

# from lecture
case "$1" in
    start)
        echo "Starting QR Security System"
        start-stop-daemon -S --exec /usr/bin/python3 /usr/bin/SecuritySystem.py
        ;;
    
    stop)
        echo "Stopping QR Security System"
        start-stop-daemon -K --signal SIGTERM
        ;;
    *)
        echo "Usage: $0 {start|stop}"
    exit 1
esac
