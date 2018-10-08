==============================================================
Script Ansible per il setup dell'infrastruttura di Docs Italia
==============================================================

role disponibili
================

* ansible: aggiunge dei requirement ansible
* app: applicazione ReadTheDocs
* certbot: installa letsencrypt e emette il certificato
* docker: docker
* es: ElasticSearch
* python: python e packages di supporto
* sql: PostgreSQL
* update: apt update
* web: Server http
* backup: Backup del database

Variabili
=========

Vedi i singoli `role` per le variabili disponibili

Variabili di infrastruttura
***************************

Sono disponibili le seguenti variabili globali (definite solitamente sull'host):

* http[=1]: Install http server
* es[=1]: Install Elasticsearch server
* python[=1]: Install python environment
* app[=1]: Install rtd
* sql[=1]: Install postgres
* converter[=1]: Install docx/odt -> RST converter
* python_version=2.7|[3.x]: Python version to be used to run rtd
* worker[=1]: Install worker-related packages (docker)
* ansible_python_interpreter[=/usr/bin/python3]: Path to python interpreter on remote
* force: general variable to force actions

Esempio::

    192.168.93.171 ansible_port=22 ansible_user=user http=1 es=1 python=1 app=1 sql=1 python_version=2.7 worker=1 docker=1 ansible_python_interpreter=/usr/bin/python2
    192.168.93.171 ansible_port=22 ansible_user=ubuntu http=1 es=1 python=1 app=1 sql=1 python_version=3.6 worker=1 docker=1 ansible_python_interpreter=/usr/bin/python3 rtd_domain=my.domain.it rtd_baseurl=my.domain.it rtd_proto=http converter=1 converter_branch=master docker_version=18.06.0~ce~3-0~ubuntu

Variabili di configurazione dell'applicazione
*********************************************

Alcune variabili sono strettamente dipendenti dall'ambiente di runtime, e i valori di defautl **non funzionano**.

Sarà quindi necessario sovrascriverle nel file ``vagrant.yml`` o nell'inventory file.

Alcuni valori sicuri per ambiente di sviluppo sono::

    SLUMBER_USERNAME: ''
    SLUMBER_PASSWORD: ''
    GITHUB_APP_ID: ''
    GITHUB_API_SECRET: ''
    USE_SMTP: False
    EMAIL_HOST: ''
    EMAIL_HOST_USER: ''
    EMAIL_HOST_PASSWORD: ''


Un esempio di inventory file potrebbe essere::

    hosts:
      hosts:
        192.168.93.170 python=1 app=1 http=1
        192.168.93.171 python=1 worker=1 docker=1
        192.168.93.172 es=1
        192.168.93.173 sql=1

      vars:
        SECRET_KEY: 'somerandomsupersecretkey'
        SLUMBER_USERNAME: 'slumber'
        SLUMBER_PASSWORD: 'slumber'
        GITHUB_APP_ID: ''
        GITHUB_API_SECRET: ''
        DOCKER_ENABLE: False
        USE_SMTP: False
        EMAIL_HOST: ''
        EMAIL_HOST_USER: ''
        EMAIL_HOST_PASSWORD: ''


Setup
=====

* Crea un virtualenv Python con i requirements installati da ``requirements.txt``
* Crea un host inventory e definisci le **variabili di infrastruttura** come mostrato sopra
* Crea un file vault nominato ``vault`` lanciando ``ansible-vault create vault``
* Aggiungi una password per criptare il vault
* Aggiungi una password alla macchina remota con ``ansible_become_pass: mysudopassword``
* Crea un file di testo contenente la password del vault (es: ``vault.txt``)
* Sovrascrivi le **variabili di configurazione dell'applicazione** come mostrato sopra
* Lancia ansible con ``ansible-playbook -i hosts --vault-password-file=vault.txt setup.yml``


Ordine dei role
===============

Se vuoi creare un playbook custom, tieni in considerazione queste dipendenze **strict**:

* ``app`` dipende da:

  * ``web``
  * ``sql``
  * ``es``
  * ``python``
  * ``docker``

* ``certbot`` dipende da:

  * ``web``

Tag disponibili
===============

* ``setup``: services installation:
    * nginx
    * elasticsearch
    * postgres
    * python interpreter
    * docker
    * pandoc / converter commands

* ``init``: inizializzazione
    * aggiornamento immagine docker

* ``configuration``: aggiornamento configurazione di sistema
    * compresi i servizi / daemon RTD

* ``deploy``: deployment applicazione Django

* ``settings``: aggiornamento settings application Django

* ``deploy_pandoc``: aggiornamento comandi conversione


pandoc / converter
==================

Questo playbook può installare anche un convertitore di documenti nel formato RST.

Esso viene installato come un'applicazione del progetto principale e sarà disponibile all'URL ``/converti``.

backup
======

Tramite il role ``backup`` è possibile installare il backup giornaliero del database. Le informazioni sul database
sono le stesse usate per il setup dell'applicazione, per cui di default non sono necessarie ulteriori opzioni.

Tag
***

Il role mette a disposizione due tag:

* ``setup``: configurazione dello script di backup e del crontab
* ``backup``: esegue il ``setup``. lancia il backup e scarica sul computer locale il backup eseguito

i tag sono disponibili sia nel playbook ``setup.yml``, sia in uno dedicato ``backup.yml``

Esempi
********

* ``ansible-playbook -i cluster backup.yml --vault-password-file=vault.txt -tsetup`` setup e configurazione del backup
* ``ansible-playbook -i cluster backup.yml --vault-password-file=vault.txt -tbackup`` esegue il backup e scarica il file in locale

Variabili
*********

A parte quelle relative alla configurazione del database condivise con il role ``app`` sono disponibili le seguenti variabili:

* ``sql_backup_history[=30]``: numero massimo di giorni per i file di backup
* ``sql_backup_dir[=/var/local/backup]``: directory locale del server dove archiviare i backup
* ``sql_backup_script[=/usr/local/sbin/backup_sql.sh]``: percorso dello script di backup

Archiviazione remota
********************

TODO

2 soluzioni possibili:

* integrare un scp nello script di backup
* montare sul server uno storage condiviso


====
TODO
====

* [ ] Handle or document data needed for a working setup

* Development except vaulted secrets
* [ ] improve multi server settings
