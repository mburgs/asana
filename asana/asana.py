#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:
    import simplejson as json
except ImportError:
    import json

from pprint import pprint


class AsanaException(Exception):
    """Wrap api specific errors"""
    pass


class AsanaAPI(object):
    """Basic wrapper for the Asana api. For further information on the API
    itself see: http://developer.asana.com/documentation/
    """

    def __init__(self, apikey, debug=False, cache=None, dry_run=False):
        """Initializes the API
        :param apikey: the API from Asana
        :param debug: If true will print out requests
        :param cache: If true will cache GET responses for the life of the script. If a number will only cache for that many seconds
        :param dry_run: If true will prevent any POST, PUT or DELETE requests from executing
        """
        self.debug = debug

        if cache:
            self.cache = Cache(cache)
        else:
            self.cache = False

        self.dry_run = dry_run

        self.asana_url = "https://app.asana.com/api"
        self.api_version = "1.0"
        self.aurl = "/".join([self.asana_url, self.api_version])
        self.apikey = apikey
        self.bauth = self.get_basic_auth()

    def get_basic_auth(self):
        """Get basic auth creds
        :returns: the basic auth string
        """
        s = self.apikey + ":"
        return s.encode("base64").rstrip()

    def handle_exception(self, r):
        """ Handle exceptions

        :param r: request object
        :returns: 1 if exception was 429 (rate limit exceeded), otherwise, -1
        """
        if self.debug:
            print "-> Got: %s" % r.status_code
            print "-> %s" % r.text
        if (r.status_code == 429):
            self._handle_rate_limit(r)
            return 1
        else:
            raise AsanaException('Received non 2xx or 404 status code on call')

    def _handle_rate_limit(self, r):
        """ Sleep for length of retry time

        :param r: request object
        """
        retry_time = int(r.headers['Retry-After'])
        assert(retry_time > 0)
        if self.debug:
            print("-> Sleeping for %i seconds" % retry_time)
        time.sleep(retry_time)

    def get(self, target, **kwargs):
        """Peform a GET request

        :param target: API URI path for request
        """

        if self.cache:
            if self.cache.has(target, **kwargs):
                if self.debug:
                    print 'CACHE {0}'.format(target)

                return self.cache.get(target, **kwargs)

        ret = self._do_request('get', target, **kwargs)

        if self.cache:
            self.cache.store(ret, target, **kwargs)

        return ret

    def delete(self, target, **kwargs):
        """Peform a DELETE request

        :param target: API URI path for request
        """
        return self._do_request('delete', target, **kwargs)

    def post(self, target, **kwargs):
        """Peform a POST request

        :param target: API URI path for request
        :param data: POST payload
        :param files: Optional file to upload
        """

        if 'data' in kwargs:
            kwargs['data'] = json.dumps({'data':kwargs['data']})

        return self._do_request('post', target, **kwargs)

    def put(self, target, **kwargs):
        """Peform a PUT request

        :param target: API URI path for request
        :param data: PUT payload
        """

        if 'data' in kwargs:
            kwargs['data'] = json.dumps({'data':kwargs['data']})
            
        return self._do_request('put', target, **kwargs)

    def _do_request(self, method, target, **kwargs):

        target = "/".join([self.aurl, target])

        if self.debug:
            print '{0} {1}'.format(method.upper(), target)
            for arg in ['params', 'data', 'files']:
                if kwargs.get(arg):
                    print '\t{0} => {1}'.format(arg, kwargs[arg])

        if self.dry_run and method != 'get':
            return {}

        r = getattr(requests, method)(target, auth=(self.apikey, ""), **kwargs)
        if self._ok_status(r.status_code) and r.status_code is not 404:
            if r.headers['content-type'].split(';')[0] == 'application/json':
                if hasattr(r, 'text'):
                    return json.loads(r.text)['data']
                elif hasattr(r, 'content'):
                    return json.loads(r.content)['data']
                else:
                    raise AsanaException('Unknown format in response from api')
            else:
                raise AsanaException(
                    'Did not receive json from api: %s' % str(r))
        else:
            if (self.handle_exception(r) > 0):
                return self._do_request(method, target, **kwargs)

    @staticmethod
    def _ok_status(status_code):
        """Check whether status_code is a ok status i.e. 2xx or 404"""
        status_code = int(status_code)
        if status_code / 200 is 1:
            return True
        elif status_code / 400 is 1:
            if status_code is 404:
                return True
            else:
                return False
        elif status_code is 500:
            return False

class Cache(object):
    def __init__(self, cachetime):
        if isinstance(cachetime, int):
            self.cachetime = cachetime
        else:
            self.cachetime = 0 #forever!

        self._cache = {}

    def has(self, target, **kwargs):
        key = self._get_key(target, **kwargs)
        item = self._cache.get(key)

        if item:
            if not self.cachetime:
                return True

            if time.time() - self.cachetime <= item['createTime']:
                return True
            else:
                del self._cache[key]

        return False

    def get(self, target, **kwargs):
        return self._cache.get(self._get_key(target, **kwargs))['value']

    def store(self, value, target, **kwargs):
        self._cache[self._get_key(target, **kwargs)] = {
            'value': value,
            'createTime': time.time()
        }

    @staticmethod
    def _get_key(target, **kwargs):
        key = target

        if kwargs.get('params'):
            key += str(kwargs['params'])

        return key