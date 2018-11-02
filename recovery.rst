Procedura di restore completo
=============================

La procedura presuppone che esista un backup completo del database di produzione e dei certificati ssl (eseguito tramite il playbook ``backup.yml``), e che sia sufficientemente recente da contenere tutti token e certificati validi

* Creare un file di inventory con la configurazione completa del sistema.
  es::

    [hosts]
    1.2.3.4 http=1 es=0 python=1 app=1 sql=0 worker=1 docker=1 converter=1 # HTTP
    1.2.3.5 http=0 es=0 python=0 app=0 sql=1 worker=0 docker=0 converter=0 # PSQL
    1.2.3.6 http=0 es=1 python=0 app=0 sql=0 worker=0 docker=0 converter=0 # ES
    [hosts:vars]
    ansible_become_pass=ubuntu
    ansible_port=22
    ansible_user=docs-admin
    python_version=3.6
    ansible_python_interpreter=/usr/bin/python3
    rtd_domain=docs.dominio.it
    rtd_baseurl=docs.dominio.it
    rtd_proto=https
    converter_app_branch=master
    docker_version=18.06.0~ce~3-0~ubuntu
    rtd_db_host=1.2.3.5
    rtd_db_pass=docs
    es_hosts="1.2.3.6"

* Fare il setup iniziale delle nuove VM::

    ansible-playbook -i my-cluster setup.yml -eforce --vault-password-file=vault.txt

* Eseguire il restore del database e dei certificati ssl::

    ansible-playbook -i recovery backup.yml -elocal_dump=<path/dump.sql.gz> -elocal_ssl=<path/tar/certificati.tar.gz> -eforce=1 --vault-password-file=vault.txt  -trestore

* Lanciare il rebuild della documentazione::

    ansible-playbook -i recovery documents.yml -eforce=1 --vault-password-file=vault.txt  -tbuild_docs

* Il rebuild può essere eseguito anche per singoli documenti / publisher, secondo quanto documentato per il playbook ``documents.yml``
