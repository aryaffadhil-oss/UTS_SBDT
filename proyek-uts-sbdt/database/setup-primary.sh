#!/bin/bash
set -e
echo "host replication repl_user 0.0.0.0/0 trust" >> "$PGDATA/pg_hba.conf"
pg_ctl -D "$PGDATA" reload