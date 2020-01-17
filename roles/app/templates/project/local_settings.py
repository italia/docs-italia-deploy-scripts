# Managed settings file

import os
import re

from readthedocs.settings.base import CommunityBaseSettings

_redis = {
    'default': dict(zip(['host', 'port', 'db'], re.split(':|/', '{{ rtd_redis_cache }}'))),
    'celery': dict(zip(['host', 'port', 'db'], re.split(':|/', '{{ rtd_redis_celery }}'))),
    'stats': dict(zip(['host', 'port', 'db'], re.split(':|/', '{{ rtd_redis_stats }}'))),
}


class CommunityProdSettings(CommunityBaseSettings):

    """Settings for local development"""
    SERVE_DOCS = ['private']
    PYTHON_MEDIA = True
    PRODUCTION_DOMAIN = '{{ rtd_domain }}'
    USE_SUBDOMAIN = False
    PUBLIC_DOMAIN = '{{ PUBLIC_DOMAIN }}'
    PUBLIC_API_URL = '{{ PUBLIC_API_URL }}'
    GLOBAL_ANALYTICS_CODE = '{{ GLOBAL_ANALYTICS_CODE }}'
    PUBLIC_DOMAIN_USES_HTTPS = '{{ rtd_proto }}' == 'https'

    # default build versions
    RTD_LATEST = 'bozza'
    RTD_LATEST_VERBOSE_NAME = RTD_LATEST
    RTD_STABLE = 'stabile'
    RTD_STABLE_VERBOSE_NAME = RTD_STABLE
    RTD_LATEST_EN = 'draft'
    RTD_STABLE_EN = 'stable'

    # General settings
    DEBUG = {{ DEBUG }}
    TEMPLATE_DEBUG = False

    DOCS_BASE = os.environ.get('DOCS_BASE', CommunityBaseSettings.SITE_ROOT)
    MEDIA_ROOT = os.path.join(DOCS_BASE, 'media/')
    STATIC_ROOT = os.path.join(DOCS_BASE, 'media/static/')
    MEDIA_URL = '{{ MEDIA_URL }}'
    STATIC_URL = '{{ MEDIA_URL }}static/'
    ADMIN_MEDIA_PREFIX = MEDIA_URL + 'admin/'
    SECRET_KEY = '{{ SECRET_KEY }}'
    DEFAULT_FROM_EMAIL = '{{ DEFAULT_FROM_EMAIL }}'
    SESSION_COOKIE_DOMAIN = '{{ rtd_domain }}'
    TAGGIT_TAGS_FROM_STRING = 'taggit.utils._parse_tags'

    DOCROOT = os.path.join(DOCS_BASE, 'user_builds')
    UPLOAD_ROOT = os.path.join(DOCS_BASE, 'user_uploads')
    CNAME_ROOT = os.path.join(DOCS_BASE, 'cnames')
    LOGS_ROOT = os.path.join(DOCS_BASE, 'logs')
    PRODUCTION_ROOT = os.path.join(DOCS_BASE, 'prod_artifacts')
    PUBLIC_BASE = DOCS_BASE
    PRIVATE_BASE = DOCS_BASE

    @property
    def TEMPLATES(self):  # noqa
        TEMPLATES = super().TEMPLATES
        TEMPLATE_OVERRIDES = os.path.join(super().TEMPLATE_ROOT, 'docsitalia', 'overrides')
        TEMPLATES[0]['DIRS'].insert(0, TEMPLATE_OVERRIDES)
        return TEMPLATES

    @property
    def INSTALLED_APPS(self):  # noqa
        apps = super(CommunityProdSettings, self).INSTALLED_APPS
        # Insert our depends above RTD applications, after guaranteed third
        # party package
        apps.append('readthedocs.docsitalia')
        apps.append('dal', )
        apps.append('dal_select2', )
        {% if USE_CONVERTER %}apps.insert(apps.index('rest_framework'), 'docs_italia_convertitore_web'){% endif %}

        {% if SENTRY_DSN|string|length %}apps.insert(apps.index('rest_framework'), 'raven.contrib.django.raven_compat'){% endif %}

        return apps

    # Celery
    CACHES = dict(
        (cache_name, {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '{host}:{port}'.format(**cache),
            'OPTIONS': {
                'DB': cache['db'],
            },
        })
        for (cache_name, cache)
        in _redis.items()
        if cache_name is not 'celery'
    )
    BROKER_URL = 'redis://{{ rtd_redis_celery }}'
    CELERY_RESULT_BACKEND = 'redis://{{ rtd_redis_celery }}'

    # Docker
    DOCKER_SOCKET = 'tcp://{{ docker_main_ip }}:2375'
    DOCKER_ENABLE = {{ DOCKER_ENABLE }}
    DOCKER_IMAGE = '{{ docker_rtd_image }}'
    DOCKER_VERSION = '1.33'
    DOCKER_LIMITS = {
        'memory': '999m',
        'time': 3600,
    }
    {% if SENTRY_DSN|string|length  %}

    import raven
    RAVEN_CONFIG = {
        'dsn': '{{ SENTRY_DSN }}',
        'release': raven.fetch_git_sha(CommunityBaseSettings.SITE_ROOT),
        'environment': '{{ SENTRY_ENVIRONMENT }}'
    }
    {% endif %}

    # Haystack - we don't really use it. ES API is used instead
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    }

    CELERY_ALWAYS_EAGER = False
    CELERY_HAYSTACK_DEFAULT_ALIAS = None
    CELERY_TASK_RESULT_EXPIRES = 7200

    # Elastic Search
    ES_HOSTS = '{{ es_hosts }}'.split(',')
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': ES_HOSTS
        },
    }

    # RTD settings
    # This goes together with FILE_SYNCER setting
    # eg: FILE_SINCER = 'readthedocs.builds.syncers.*' (likely RemoteSyncer)
    MULTIPLE_APP_SERVERS = '{{ app_hosts }}'.split(',')
    MULTIPLE_BUILD_SERVERS = '{{ worker_hosts }}'.split(',')
    SLUMBER_API_HOST = 'http://{{ api_host }}'
    SLUMBER_USERNAME = '{{ SLUMBER_USERNAME }}'
    SLUMBER_PASSWORD = '{{ SLUMBER_PASSWORD }}'
    SYNC_USER = '{{ rtd_user }}'
    #DOCROOT = '/var/build'

    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    REPO_LOCK_SECONDS = 300
    DONT_HIT_DB = False

    # Override classes
    CLASS_OVERRIDES = {
        'readthedocs.builds.syncers.Syncer': 'readthedocs.builds.syncers.LocalSyncer',
        'readthedocs.core.resolver.Resolver': 'readthedocs.docsitalia.resolver.ItaliaResolver',
        'readthedocs.oauth.services.GitHubService': 'readthedocs.docsitalia.oauth.services.github.DocsItaliaGithubService',
    }

    # Email
    if {{ USE_SMTP }}:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_USE_TLS = True
        EMAIL_HOST = '{{ EMAIL_HOST }}'
        EMAIL_HOST_USER = '{{ EMAIL_HOST_USER }}'
        EMAIL_HOST_PASSWORD = '{{ EMAIL_HOST_PASSWORD }}'
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # Social Auth
    GITHUB_APP_ID = '{{ GITHUB_APP_ID }}'
    GITHUB_API_SECRET = '{{ GITHUB_API_SECRET }}'

    SOCIALACCOUNT_PROVIDERS = {
        'github': {'SCOPE': ['user:email', 'read:org', 'admin:repo_hook', 'repo:status']}
    }

    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

    ADMINS = (
        ('Test', 'test@{{ rtd_domain }}'),
    )
    TIME_ZONE = 'Europe/Rome'
    LANGUAGE_CODE = 'it-it'

    CORS_ORIGIN_WHITELIST = (
        '{{ rtd_domain }}:8000',
    )

{% if CORS_HEADERS_HOSTS == 'all' %}
    CORS_ORIGIN_ALLOW_ALL = True
{% endif %}

    WEBSOCKET_HOST = '{{ rtd_domain }}:8088'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '{{ rtd_db_name }}',
            'USER': '{{ rtd_db_user }}',
            'PASSWORD': '{{ rtd_db_pass }}',
            'HOST': '{{ rtd_db_host }}',
            'PORT': '{{ rtd_db_port }}',
        },
    }

    # Etc
    RESTRUCTUREDTEXT_FILTER_SETTINGS = {
        'cloak_email_addresses': True,
        'file_insertion_enabled': False,
        'raw_enabled': False,
        'strip_comments': True,
        'doctitle_xform': True,
        'sectsubtitle_xform': True,
        'initial_header_level': 2,
        'report_level': 5,
        'syntax_highlight': 'none',
        'math_output': 'latex',
        'field_name_limit': 50,
    }
    USE_PROMOS = False

    ALLOWED_HOSTS = ['*']
    USER_MATURITY_DAYS = 14
    READTHEDOCSEXT_MONITORING_CACHE = 'stats'
    DEFAULT_VERSION_PRIVACY_LEVEL = '{{ DEFAULT_VERSION_PRIVACY_LEVEL }}'

    @property
    def TEXTCLASSIFIER_DATA_FILE(self):
        return os.path.join(self.SITE_ROOT, 'textclassifier.json')

    # Banned" projects
    HTML_ONLY_PROJECTS = (
        'atom',
        'galaxy-central',
        'django-geoposition',
    )

    # Add fancy sessions after the session middleware
    @property
    def MIDDLEWARE(self):
        classes = super(CommunityProdSettings, self).MIDDLEWARE
        classes = list(classes)
        index = classes.index(
            'readthedocs.core.middleware.FooterNoSessionMiddleware'
        )
        classes.insert(
            index + 1,
            'restrictedsessions.middleware.RestrictedSessionsMiddleware'
        )
        return tuple(classes)

    RESTRICTEDSESSIONS_AUTHED_ONLY = True

    # Logging
    @property
    def LOGGING(self):
        logging = super(CommunityProdSettings, self).LOGGING
        logging['formatters']['syslog'] = {
            'format': 'readthedocs/%(name)s[%(process)d]: %(levelname)s %(message)s [%(name)s:%(lineno)s]',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        }
        logging['handlers']['syslog'] = {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'syslog',
            'address': '/dev/log',
        }
        logging['loggers'] = {
            '': {
                'handlers': ['console', 'syslog'],
                'level': 'INFO',
            }
        }
        return logging


CommunityProdSettings.load_settings(__name__)

if not os.environ.get('DJANGO_SETTINGS_SKIP_LOCAL', False):
    try:
        # pylint: disable=unused-wildcard-import
        from .local_settings import *  # noqa
    except ImportError:
        pass
