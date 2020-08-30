import time
import hmac
import json
import httplib2
from urllib.parse import urlparse, urlsplit, urlencode, quote_plus

import mimetypes

from io import StringIO

__all__ = ['AdflyApi']

def getDictionary():
    extension_to_mimetype = {}
    mimetype_to_extension = {
        'text/plain': 'txt',
        'text/xml': 'xml',
        'text/css': 'css',
        'text/javascript': 'js',
        'text/rtf': 'rtf',
        'text/calendar': 'ics',
        'application/msword': 'doc',
        'application/msexcel': 'xls',
        'application/x-msword': 'doc',
        'application/vnd.ms-excel': 'xls',
        'application/vnd.ms-powerpoint': 'ppt',
        'application/pdf': 'pdf',
        'text/comma-separated-values': 'csv',
        'image/jpeg': 'jpg',
        'image/gif': 'gif',
        'image/jpg': 'jpg',
        'image/tiff': 'tiff',
        'image/png': 'png'
    }

    # And hacky reverse lookups
    for mimetype in mimetype_to_extension:
        extension_to_mimetype[mimetype_to_extension[mimetype]] = mimetype

    mimetype_extension_mapping = {}
    mimetype_extension_mapping.update(mimetype_to_extension)
    mimetype_extension_mapping.update(extension_to_mimetype)

    return mimetype_extension_mapping


class ConnectionError(Exception):
    def __str__(self):
        return "Connection failed"


class Connection:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.username = username
        self.mimetypes = getDictionary()

        self.url = urlparse(base_url)

        (scheme, netloc, path, query, fragment) = urlsplit(base_url)

        self.scheme = scheme
        self.host = netloc
        self.path = path

        # Create Http class with support for Digest HTTP Authentication, if necessary
        self.h = httplib2.Http(".cache")
        self.h.follow_all_redirects = True
        if username and password:
            self.h.add_credentials(username, password)

    def request_get(self, resource, args=None, headers={}):
        return self.request(resource, "get", args, headers=headers)

    def request_delete(self, resource, args=None, headers={}):
        return self.request(resource, "delete", args, headers=headers)

    def request_head(self, resource, args=None, headers={}):
        return self.request(resource, "head", args, headers=headers)

    def request_post(self, resource, args=None, body=None, filename=None, headers={}):
        return self.request(resource, "post", args, body=body, filename=filename, headers=headers)

    def request_put(self, resource, args=None, body=None, filename=None, headers={}):
        return self.request(resource, "put", args, body=body, filename=filename, headers=headers)

    def get_content_type(self, filename):
        extension = filename.split('.')[-1]
        guessed_mimetype = self.mimetypes.get(
            extension, mimetypes.guess_type(filename)[0])
        return guessed_mimetype or 'application/octet-stream'

    def request(self, resource, method="get", args=None, body=None, filename=None, headers={}):
        params = None
        path = resource
        headers['User-Agent'] = 'Basic Agent'

        BOUNDARY = u'00hoYUXOnLD5RQ8SKGYVgLLt64jejnMwtO7q8XE1'
        CRLF = u'\r\n'

        if filename and body:
            #fn = open(filename ,'r')
            #chunks = fn.read()
            # fn.close()

            # Attempt to find the Mimetype
            content_type = self.get_content_type(filename)
            headers['Content-Type'] = 'multipart/form-data; boundary=' + BOUNDARY
            encode_string = StringIO()
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + CRLF)
            encode_string.write(
                u'Content-Disposition: form-data; name="file"; filename="%s"' % filename)
            encode_string.write(CRLF)
            encode_string.write(u'Content-Type: %s' % content_type + CRLF)
            encode_string.write(CRLF)
            encode_string.write(body)
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + u'--' + CRLF)

            body = encode_string.getvalue()
            headers['Content-Length'] = str(len(body))
        elif body:
            if not headers.get('Content-Type', None):
                headers['Content-Type'] = 'text/xml'
            headers['Content-Length'] = str(len(body))
        else:
            if 'Content-Length' in headers:
                del headers['Content-Length']

            headers['Content-Type'] = 'text/plain'

            if args:
                if method in ("get", 'delete'):
                    path += u"?" + urlencode(args)
                elif method == "put" or method == "post":
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    body = urlencode(args)

        request_path = []
        # Normalise the / in the url path
        if self.path != "/":
            if self.path.endswith('/'):
                request_path.append(self.path[:-1])
            else:
                request_path.append(self.path)
            if path.startswith('/'):
                request_path.append(path[1:])
            else:
                request_path.append(path)

        resp, content = self.h.request(u"%s://%s%s" % (self.scheme, self.host, u'/'.join(
            request_path)), method.upper(), body=body, headers=headers)
        # TODO trust the return encoding type in the decode?
        return {u'headers': resp, u'body': content.decode('UTF-8')}


class AdflyApi:

    def __init__(self, secret_key, public_key, user_id, base_host='https://api.adf.ly'):

        self.BASE_HOST = base_host
        # TODO: Replace this with your secret key.
        self.SECRET_KEY = secret_key
        # TODO: Replace this with your public key.
        self.PUBLIC_KEY = public_key
        # TODO: Replace this with your user id.
        self.USER_ID = user_id
        self.AUTH_TYPE = dict(basic=1, hmac=2)

        # In this example we use rest client provided by
        # http://code.google.com/p/python-rest-client/
        # Of course you are free to use any other client.
        self._connection = Connection(self.BASE_HOST)

    def get_groups(self, page=1):
        response = self._connection.request_get(
            '/v1/urlGroups',
            args=self._get_params(dict(_page=page), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])

    def expand(self, urls, hashes=[]):
        params = dict()

        if type(urls) == list:
            for i, url in enumerate(urls):
                params['url[%d]' % i] = url
        elif type(urls) == str:
            params['url'] = urls

        if type(hashes) == list:
            for i, hashval in enumerate(hashes):
                params['hash[%d]' % i] = hashval
        elif type(hashes) == str:
            params['hash'] = hashes

        response = self._connection.request_get(
            '/v1/expand',
            args=self._get_params(params, self.AUTH_TYPE['basic']))
        return json.loads(response['body'])

    def shorten(self, urls, domain=None, advert_type=None, group_id=None):
        params = dict()
        if domain:
            params['domain'] = domain
        if advert_type:
            params['advert_type'] = advert_type
        if group_id:
            params['group_id'] = group_id

        if type(urls) == list:
            for i, url in enumerate(urls):
                params['url[%d]' % i] = url
        elif type(urls) == str:
            params['url'] = urls

        response = self._connection.request_post(
            '/v1/shorten',
            args=self._get_params(params, self.AUTH_TYPE['basic']))
        return json.loads(response['body'])

    def get_urls(self, page=1, search_str=None):
        response = self._connection.request_get(
            '/v1/urls',
            args=self._get_params(dict(_page=page, q=search_str), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])

    def update_url(self, url_id, **kwargs):
        params = dict()

        allowed_kwargs = ['url', 'advert_type', 'title',
                          'group_id', 'fb_description', 'fb_image']
        for k, v in kwargs.items():
            if k in allowed_kwargs:
                params[k] = v

        response = self._connection.request_put(
            '/v1/urls/%d' % url_id,
            args=self._get_params(params, self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])

    def delete_url(self, url_id):
        response = self._connection.request_delete(
            '/v1/urls/%d' % url_id,
            args=self._get_params(dict(), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])

    def _get_params(self, params={}, auth_type=None):
        """Populates request parameters with required parameters,
        such as _user_id, _api_key, etc.
        """
        auth_type = auth_type or self.AUTH_TYPE['basic']

        params['_user_id'] = self.USER_ID
        params['_api_key'] = self.PUBLIC_KEY

        if self.AUTH_TYPE['basic'] == auth_type:
            pass
        elif self.AUTH_TYPE['hmac'] == auth_type:
            # Get current unix timestamp (UTC time).
            params['_timestamp'] = int(time.time())
            params['_hash'] = self._do_hmac(params)
        else:
            raise RuntimeError

        return params

    def _do_hmac(self, params):
        if type(params) != dict:
            raise RuntimeError

        # Get parameter names.
        keys = params.keys()
        # Sort them using byte ordering.
        # So 'param[10]' comes before 'param[2]'.
        keys.sort()
        queryParts = []

        # Url encode query string. The encoding should be performed
        # per RFC 1738 (http://www.faqs.org/rfcs/rfc1738)
        # which implies that spaces are encoded as plus (+) signs.
        for key in keys:
            quoted_key = quote_plus(str(key))
            if params[key] is None:
                params[key] = ''

            quoted_value = quote_plus(str(params[key]))
            queryParts.append('%s=%s' % (quoted_key, quoted_value))

        return hmac.new(
            self.SECRET_KEY,
            '&'.join(queryParts),
            hashlib.sha256).hexdigest()

if __name__ == '__main__':
    main()
