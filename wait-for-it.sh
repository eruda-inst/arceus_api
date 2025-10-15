#!/usr/bin/env bash
# wait-for-it.sh: Wait until a host and port are available
# Usage: wait-for-it.sh host:port -- command args

set -e

host="$1"
shift

host_name="${host%%:*}"
port="${host##*:}"

while ! nc -z "$host_name" "$port"; do
  echo "Waiting for $host_name:$port..."
  sleep 1
done

echo "$host_name:$port is available. Starting application."
exec "$@"
