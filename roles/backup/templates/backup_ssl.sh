#!/usr/bin/env bash

set -e

DATE=`date +"%Y%m%d-%H%M%S"`
BACKUP_FILE="{{ backup_dir }}/docs-ssl-${DATE}.tar.gz"

find {{ backup_dir }} -ctime +{{ backup_history }}

cd /etc
tar -czf ${BACKUP_FILE} letsencrypt

echo $BACKUP_FILE
