#!/usr/bin/env python

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

    def __init__(self, apikey, debug=False, cache=None):
        self.debug = debug

        if cache:
            self.cache = Cache(cache)
        else:
            self.cache = False

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

    def get(self, api_target, **kwargs):
        """Peform a GET request

        :param api_target: API URI path for request
        """
        return self._do_request('get', api_target, **kwargs)

    def delete(self, api_target, **kwargs):
        """Peform a DELETE request

        :param api_target: API URI path for request
        """
        return self._do_request('delete', api_target, **kwargs)

    def post(self, api_target, **kwargs):
        """Peform a POST request

        :param api_target: API URI path for request
        :param data: POST payload
        :param files: Optional file to upload
        """
        return self._do_request('post', api_target, **kwargs)

    def put(self, api_target, **kwargs):
        """Peform a PUT request

        :param api_target: API URI path for request
        :param data: PUT payload
        """        
        return self._do_request('put', api_target, **kwargs)

    def _do_request(self, method, target, **kwargs):

        target = "/".join([self.aurl, target])

        if self.cache:
            if self.cache.has(method, target, **kwargs):
                if self.debug:
                    print 'Loading {} {} from cache'.format(method.upper(), target)

                return self.cache.get(method, target, **kwargs)

        if self.debug:
            print '{} {}'.format(method.upper(), target)
            for arg in ['params', 'data', 'files']:
                if kwargs.get(arg):
                    print '\t{} => {}'.format(arg, kwargs[arg])

        r = getattr(requests, method)(target, auth=(self.apikey, ""), **kwargs)
        if self._ok_status(r.status_code) and r.status_code is not 404:
            if r.headers['content-type'].split(';')[0] == 'application/json':
                if hasattr(r, 'text'):
                    ret = json.loads(r.text)['data']
                elif hasattr(r, 'content'):
                    ret = json.loads(r.content)['data']
                else:
                    raise AsanaException('Unknown format in response from api')
            else:
                raise AsanaException(
                    'Did not receive json from api: %s' % str(r))
        else:
            if (self.handle_exception(r) > 0):
                return self._do_request(method, target, **kwargs)

        if self.cache:
            self.cache.store(ret, method, target, **kwargs)

        return ret

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

    def has(self, method, target, **kwargs):
        key = self._get_key(method, target, **kwargs)
        item = self._cache.get(key)

        if item:
            if not self.cachetime:
                return True

            if time.time() - self.cachetime <= item['createTime']:
                return True
            else:
                del self._cache[key]

        return False

    def get(self, method, target, **kwargs):
        return self._cache.get(self._get_key(method, target, **kwargs))['value']

    def store(self, value, method, target, **kwargs):
        self._cache[self._get_key(method, target, **kwargs)] = {
            'value': value,
            'createTime': time.time()
        }

    @staticmethod
    def _get_key(method, target, **kwargs):
        key = method + target

        for arg in ['data', 'params', 'files']:
            if kwargs.get(arg):
                key += str(kwargs[arg])

        return key