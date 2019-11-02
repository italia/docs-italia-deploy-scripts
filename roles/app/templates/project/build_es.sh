#!/usr/bin/env bash
# This allows to run the rebuild_projects management command in a screen session to easily launch batch document rebuild
set -e

cd {{ rtd_root }}
CMD="{{ rtd_virtualenv }}/bin/python"
COMMAND="{{ rtd_root }}/manage.py reindex_elasticsearch --settings={{ django_settings_module }}"

if [[ `whoami` == "root" ]]; then
    wait-for-it -s -t 300 192.168.93.68:9200 -- sudo -u docs ${CMD} ${COMMAND} ${@:1}
else
    wait-for-it -s -t 300 192.168.93.68:9200 -- ${CMD} ${COMMAND} ${@:1}
fi
