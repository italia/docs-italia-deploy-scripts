#!/usr/bin/env bash

set -e

DATE=`date +"%Y%m%d-%H%M%S"`
BACKUP_FILE="{{ backup_dir }}/docs-${DATE}.sql.gz"

if [[ "$1" == "delete" ]]; then
  find {{ backup_dir }} -ctime +{{ backup_history }} -delete
fi

pg_dump -h {{ rtd_db_host|default('localhost', true) }} -p {{ rtd_db_port }} -U {{ rtd_db_user }} {{ rtd_db_name }} | gzip -9c > $BACKUP_FILE

echo $BACKUP_FILE
