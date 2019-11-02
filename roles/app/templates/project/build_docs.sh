#!/usr/bin/env bash
# This allows to run the rebuild_projects management command in a screen session to easily launch batch document rebuild
set -e

cd {{ rtd_root }}
CMD="{{ rtd_virtualenv }}/bin/python"
COMMAND="{{ rtd_root }}/manage.py update_repos -f --settings={{ django_settings_module }}"

if [[ `whoami` == "root" ]]; then
  sudo -u docs ${CMD} ${COMMAND} ${@:1}
else
  ${CMD} ${COMMAND} ${@:1}
fi
