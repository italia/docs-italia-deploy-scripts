#!/usr/bin/env bash

set -e

DATE=`date +"%Y%m%d-%H%M%S"`
BACKUP_FILE="{{ backup_dir }}/docs-ssl-${DATE}.tar.gz"

if [[ "$1" == "delete" ]]; then
  find {{ backup_dir }} -ctime +{{ backup_history }} -delete
fi

cd /etc
tar -czf ${BACKUP_FILE} letsencrypt

echo $BACKUP_FILE
