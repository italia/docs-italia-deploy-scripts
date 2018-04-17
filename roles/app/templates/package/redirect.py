# -*- coding: utf-8 -*-
"""
A Flask app for redirecting documentation from the root / URL.
"""

from __future__ import division, print_function, unicode_literals

import io
import json
import os
import argparse

from flask import Flask, make_response, redirect, request, abort


app = Flask(__name__)

app.config.update({
    'DOMAIN': 'readthedocs.org',
    'SITE_ROOT': '/home/docs/checkouts/readthedocs.org/',
    'DEBUG': False,
})

app.config.from_envvar('READTHEDOCS_REDIRECT_SETTINGS', silent=True)

SINGLE_VERSION_STATUS_CODE = 418


def load_metadata(path):
    """Load metadata from file

    If metadata could not be loaded, either because there was a problem opening
    the metadata file or because there was an issue with parsing, return a
    dictionary with sane defaults.

    :param path: path to metadata file
    :returns: dictionary of metadata
    :rtype: dict
    """
    metadata_json = {}
    try:
        metadata_json = json.load(io.open(path))
    except (IOError, ValueError) as e:
        app.logger.error('Error loading project metadata: path=%s', path,
                         exc_info=True)
        return None
    return {
        'version': metadata_json.get('version', 'latest'),
        'language': metadata_json.get('language', 'en'),
        'single_version': metadata_json.get('single_version', False),
    }


@app.route('/')
def redirect_front():
    slug = None
    cname = None
    path = None
    is_subdomain = is_cname = False

    app.logger.debug("Got request for host: %s", request.host)
    if app.config['DOMAIN'] in request.host:
        is_subdomain = True
        slug = request.host.split('.')[0]
        path = os.path.join(app.config['SITE_ROOT'], 'user_builds', slug,
                            'metadata.json')
    else:
        try:
            cname = request.host.split(':')[0]
        except IndexError:
            cname = request.host
        is_cname = True
        path = os.path.join(app.config['SITE_ROOT'], 'public_cname_project',
                            cname, 'metadata.json')

    metadata = load_metadata(path)
    if metadata is None:
        abort(404)

    if slug is not None:
        metadata['slug'] = slug

    if request.query_string:
        metadata['query_string'] = '?{}'.format(request.query_string.decode('utf8'))
    else:
        metadata['query_string'] = ''

    if metadata.get('single_version', False):  # pylint: disable=no-else-return
        return make_response('', SINGLE_VERSION_STATUS_CODE)
    else:
        url = '/{language}/{version}/{query_string}'.format(**metadata)
        app.logger.debug("Redirecting %s to %s", request.host, url)
        return redirect(url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-D', '--domain', dest='domain', action='store',
                        help='Domain to host subdomains on')
    parser.add_argument('-H', '--host', dest='host', action='store',
                        help='Address to bind server to')
    parser.add_argument('-p', '--port', dest='port', action='store',
                        help='Port to bind server to')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Debug mode')

    args = parser.parse_args()
    kwargs = {}
    if args.domain is not None:
        app.config['DOMAIN'] = args.domain
    if args.host is not None:
        kwargs['host'] = args.host
    if args.port is not None:
        kwargs['port'] = int(args.port)
    if args.debug:
        app.config['DEBUG'] = True
        app.logger.setLevel(10)

    app.run(**kwargs)
