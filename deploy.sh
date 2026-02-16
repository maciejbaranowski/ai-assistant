#!/bin/bash

USER="root"
HOST="robert127.mikrus.xyz"
DEST_DIR="/root/website/"

echo "🚀 Start wdrożenia na $HOST..."

rsync -avz --delete --exclude='.git' --exclude='.venv' -e "ssh -p 10127" ./ $USER@$HOST:$DEST_DIR

ssh -p 10127 $USER@$HOST "cd $DEST_DIR && docker compose up -d --build"

echo "✅ Gotowe!"