===================================================
Ansible scripts to setup docs.italia infrastructure
===================================================

Available roles
===============

* ansible: add ansible requirements on the remote
* app: rtd app
* certbot: letsencrypt installation and certificate issue
* docker: docker
* es: Elastic Search
* python: python and support packages
* sql: postgres
* update: routine apt update
* web: http server

Variables
=========

see individual roles for available variables

Infrastructure variables
************************

The following global variables (tipically to be defined on the hosts) are available

* http[=1]: Install http server
* es[=1]: Install Elasticsearch server
* python[=1]: Install python environment
* app[=1]: Install rtd
* sql[=1]: Install postgres
* python_version=2.7|[3.x]: Python version to be used to run rtd
* worker[=1]: Install worker-related packages (docker)
* ansible_python_interpreter[=/usr/bin/python3]: Path to python interpreter on remote
* force: general variable to force actions

Example::

    192.168.93.171 ansible_port=22 ansible_user=user http=1 es=1 python=1 app=1 sql=1 python_version=2.7 worker=1 docker=1 ansible_python_interpreter=/usr/bin/python2


Application configuration variables
***********************************

Some variables are strictly dependent on the running environment, and the defaults provided here **wont't** work.

You will have to override the variables in the ``vagrant.yml`` file or the inventory file.

Safe defaults for a local environment are::

    SLUMBER_USERNAME: ''
    SLUMBER_PASSWORD: ''
    GITHUB_APP_ID: ''
    GITHUB_API_SECRET: ''
    USE_SMTP: False
    EMAIL_HOST: ''
    EMAIL_HOST_USER: ''
    EMAIL_HOST_PASSWORD: ''


Setup
=====

* Create a virtualenv with requirements installed from ``requirements.txt``
* Create a host inventory and provide the **Infrastructure variables provided above**
* Create a vault file named ``vault`` by running ``ansible-vault create vault``
* Provide a password to encrypt the vault
* Add the remote machine password as ``ansible_become_pass: mysudopassword``
* Create a text file containing the vault password (es: ``vault.txt``)
* Override the **Application configuration variables** as described above
* Run ansible with ``ansible-playbook -i hosts --vault-password-file=vault.txt setup.yml``


Available tags
==============

* setup: services installation:
    * nginx
    * elasticsearch
    * postgres
    * python interpreter
    * docker

* init: data initialization
    * pull docker image

* configuration: configuration updates
    * services configuration for rtd projects

* deploy: application deployment
    * django projects deployment

====
TODO
====

* [ ] Handle or document data needed for a working setup
* [ ] move italia_rtd to official repo
* [x] Documentation URL has https hardcoded (from italia_rtd.resolver.ItaliaResolver.resolve)
* [x] nginx configuration files cleanup / refactoring
* [x] should default variable target a development or production host type?

    * Development except vaulted secrets
* [x] move redirect app and some missing python deps in the repos
* [x] improve variable placement / naming
* [ ] improve multi server settings
* [x] improve how django management commands are run
* [x] should docker image be pulled during default installation? It's a long process (3GB+ image)
