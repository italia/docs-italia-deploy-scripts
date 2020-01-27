#!/usr/bin/env bash
# This allows to run the rebuild_projects management command in a screen session to easily launch batch document rebuild
set -e

cd {{ rtd_root }}
CMD="{{ rtd_virtualenv }}/bin/python"
COMMAND="{{ rtd_root }}/manage.py search_index --rebuild --settings={{ django_settings_module }}"

if [[ `whoami` == "root" ]]; then
    wait-for-it -s -t 300 {{ es_hosts }} -- sudo -u docs ${CMD} ${COMMAND} ${@:1}
else
    wait-for-it -s -t 300 {{ es_hosts }} -- ${CMD} ${COMMAND} ${@:1}
fi
