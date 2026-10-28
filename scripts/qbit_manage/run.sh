#!/bin/sh
# Cron entry point (every 30 min, see docs/06): tag library copies "keep", then run qbit_manage once.
# If keep_copies.py fails for any reason, qbit_manage does not run.
cd "$(dirname "$0")/../.." || exit 1
APPDATA_DIR=$(sed -n 's/^APPDATA_DIR=//p' .env | tail -n 1)
mkdir -p "$APPDATA_DIR/qbit_manage/logs"
exec 9>/tmp/qbit_manage.lock
flock -n 9 || exit 0
/usr/bin/python3 scripts/qbit_manage/keep_copies.py >> "$APPDATA_DIR/qbit_manage/logs/keep_copies.log" 2>&1 \
  && /usr/bin/docker start -a qbit_manage > /dev/null 2>&1
