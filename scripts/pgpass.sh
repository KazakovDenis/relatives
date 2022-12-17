#!/usr/bin/env bash

PGPASSFILE=${PGPASSFILE:=/opt/.pgpass}

# credentials for pg_dump to skip password passing
echo "localhost:5432:${DB_NAME}:${DB_USER}:${DB_PASS}" > $PGPASSFILE
chmod 0600 $PGPASSFILE
