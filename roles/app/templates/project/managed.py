# Managed settings file

import os
import re

from .base import CommunityBaseSettings

_redis = {
    'default': dict(zip(['host', 'port', 'db'], re.split(':|/', '{{ rtd_redis_cache }}'))),
    'celery': dict(zip(['host', 'port', 'db'], re.split(':|/', '{{ rtd_redis_celery }}'))),
    'stats': dict(zip(['host', 'port', 'db'], re.split(':|/', '{{ rtd_redis_stats }}'))),
}


class CommunityProdSettings(CommunityBaseSettings):

    """Settings for local development"""

    PRODUCTION_DOMAIN = 'dashboard.{{ rtd_domain }}'
    USE_SUBDOMAIN = False
    PUBLIC_DOMAIN = '{{ PUBLIC_DOMAIN }}'
    PUBLIC_API_URL = '{{ PUBLIC_API_URL }}'

    # General settings
    DEBUG = {{ DEBUG }}
    TEMPLATE_DEBUG = False

    MEDIA_URL = '{{ MEDIA_URL }}'
    STATIC_URL = '{{ MEDIA_URL }}static/'
    ADMIN_MEDIA_PREFIX = MEDIA_URL + 'admin/'
    SECRET_KEY = '{{ SECRET_KEY }}'
    DEFAULT_FROM_EMAIL = '{{ DEFAULT_FROM_EMAIL }}'
    SESSION_COOKIE_DOMAIN = '{{ rtd_domain }}'
    # riccardo: need this atm
    #ALLOW_ADMIN = False

    @property
    def INSTALLED_APPS(self):  # noqa
        apps = super(CommunityProdSettings, self).INSTALLED_APPS
        # riccardo: HACK, don't add proprietary extensions
        #apps.extend([
        #    'readthedocsext.monitoring',
        #])
        # Insert our depends above RTD applications, after guaranteed third
        # party package
        apps.insert(apps.index('rest_framework'), 'italia_rtd')
        # riccardo: HACK, remove extensions while we still have them
        apps = [a for a in apps if a not in ('django_countries', 'readthedocsext.donate', 'readthedocsext.embed')]
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
    DOCKER_ENABLE = True
    DOCKER_IMAGE = '{{ docker_rtd_image }}'
    DOCKER_VERSION = '1.33'
    DOCKER_LIMITS = {
        'memory': '999m',
        'time': 3600,
    }

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

    # Don't require email verification, but send verification email.
    ACCOUNT_EMAIL_VERIFICATION = 'optional'
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    # SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    REPO_LOCK_SECONDS = 300
    DONT_HIT_DB = False

    # Override classes
    CLASS_OVERRIDES = {
        'readthedocs.builds.syncers.Syncer': 'readthedocs.builds.syncers.LocalSyncer',
        'readthedocs.core.resolver.Resolver': 'italia_rtd.resolver.ItaliaResolver',
        'readthedocs.oauth.services.GitHubService': 'docsitalia.oauth.services.github.DocsItaliaGithubService',
    }

    # Email
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
    def MIDDLEWARE_CLASSES(self):
        classes = super(CommunityProdSettings, self).MIDDLEWARE_CLASSES
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
            'datefmt' : '%d/%b/%Y %H:%M:%S'
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
