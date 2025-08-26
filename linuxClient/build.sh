#!/bin/bash

# Backup client.py
cp client.py client.py.bak

# Function to restore client.py from backup
cleanup() {
    echo "Restoring client.py from backup."
    mv client.py.bak client.py
}

# Register cleanup function to be called on script exit
trap cleanup EXIT

# Extract token from .env file and replace in client.py
if [ -f "../server/.env" ]; then
    AUTH_TOKEN_SECRET=$(awk -F= '/^AUTH_TOKEN_SECRET/ {gsub(/[[:space:]]/, "", $2); print $2}' ../server/.env)

    if [ -n "$AUTH_TOKEN_SECRET" ]; then
        sed -i "s|AUTH_TOKEN_SECRET_TO_REPLACE|$AUTH_TOKEN_SECRET|g" client.py
        echo "AUTH_TOKEN_SECRET replaced in client.py"
    else
        echo "Warning: AUTH_TOKEN_SECRET not found or is empty in ../server/.env"
    fi
else
    echo "Warning: ../server/.env file not found."
fi

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pyinstaller client.spec
echo "Build finished. The binary is located in the dist/ directory."

# Explicitly call cleanup and remove the trap
cleanup
trap - EXIT
