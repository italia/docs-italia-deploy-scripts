#!/usr/bin/env bash
# This allows to run the rebuild_projects management command in a screen session to easily launch batch document rebuild
set -e

cd ${HOME}
CMD="{{ rtd_virtualenv }}/bin/python"
COMMAND="{{ rtd_root }}/manage.py rebuild_projects --settings=readthedocs.settings.managed --async"

${CMD} ${COMMAND} ${@:1}
