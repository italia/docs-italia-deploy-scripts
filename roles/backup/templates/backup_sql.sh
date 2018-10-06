#!/usr/bin/env bash

set -e

DATE=`date +"%Y%m%d-%H%M%S"`
BACKUP_FILE="{{ sql_backup_dir }}/docs-${DATE}.sql.gz"

find {{ sql_backup_dir }} -ctime +{{ sql_backup_history }}

pg_dump -h {{ rtd_db_host }} -p {{ rtd_db_port }} -U {{ rtd_db_user }} {{ rtd_db_name }} | gzip -9c > $BACKUP_FILE

echo $BACKUP_FILE
