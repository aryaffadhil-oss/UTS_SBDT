#!/bin/bash
set -e

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "Menunggu db-primary siap..."
  until pg_isready -h db-primary -p 5432 -U postgres; do
    sleep 2
  done

  echo "Menjalankan pg_basebackup dari db-primary..."
  PGPASSWORD=repl_pass pg_basebackup -h db-primary -D "$PGDATA" -U repl_user -v -P -R -X stream -S replica_slot
  chown -R postgres:postgres "$PGDATA"
  chmod 0700 "$PGDATA"
fi

exec docker-entrypoint.sh postgres