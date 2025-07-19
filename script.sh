#!/bin/bash

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python not installed"
        exit 1
    fi
fi

if ! python3 -c "import rich" 2>/dev/null; then
    echo "Installing rich..."
    sudo pip3 install rich
fi

if ! python3 -c "import rich" 2>/dev/null; then
    echo "Error: Failed to install rich"
    exit 1
fi 



sudo python3 snitch.py "$@"