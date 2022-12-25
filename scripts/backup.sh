#!/usr/bin/env bash

SSH_HOST=vps
SOURCE_FILE="/opt/relatives/dump/postgresql/relatives.tar"
TARGET_DIR="/media/share/denis/projects/relatives"
DB_DUMP_DIR="$TARGET_DIR/postgresql"
MEDIA_DIR="$TARGET_DIR/uploads"

# backup db dump
ssh $SSH_HOST "
    cd /opt/relatives && \
    docker compose exec postgres sh -c \"pg_dump -U relatives -F t relatives > /opt/dump/relatives.tar\" \
"
scp $SSH_HOST:$SOURCE_FILE $DB_DUMP_DIR/relatives.tar
mv $DB_DUMP_DIR/relatives.tar $DB_DUMP_DIR/"$(date +%F -r $DB_DUMP_DIR/relatives.tar)".tar

# backup media files
rclone --log-level INFO --log-file /var/log/rclone/relatives.log --progress sync vps:/opt/relatives/uploads $MEDIA_DIR
