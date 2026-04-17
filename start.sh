#!/usr/bin/env sh
set -e
cd /app
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  .venv/bin/alembic -c alembic.ini upgrade head
fi
exec "$@"