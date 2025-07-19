#!/bin/bash

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not installed"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 not installed"
    exit 1
fi

if ! python3 -c "import rich" 2>/dev/null; then
    echo "Installing rich..."
    pip3 install --user rich
    if ! python3 -c "import rich" 2>/dev/null; then
        echo "Error: Failed to install rich"
        exit 1
    fi
fi

echo "$(date): Running snitch.py with args $@" >> snitch.log

python3 snitch.py "$@"