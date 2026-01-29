from builtins import str
from builtins import object
import requests


class TARestHelper(object):
    def __init__(self, logger=None):
        self.logger = logger
        self.http_session = None
        self.requests_proxy = None

    def _init_request_session(self, proxy_uri=None):
        self.http_session = requests.Session()
        self.http_session.mount(
            'http://', requests.adapters.HTTPAdapter(max_retries=3))
        self.http_session.mount(
            'https://', requests.adapters.HTTPAdapter(max_retries=3))
        if proxy_uri:
            self.requests_proxy = {'http': proxy_uri, 'https': proxy_uri}
            # Log proxy URI without credentials for security
            safe_uri = proxy_uri.split('@')[-1] if '@' in proxy_uri else proxy_uri
            if self.logger:
                self.logger.debug('Initializing HTTP session with proxy: {0}'.format(safe_uri))

    def send_http_request(self, url, method, parameters=None, payload=None, headers=None, cookies=None, verify=True,
                          cert=None, timeout=None, proxy_uri=None):
        if self.http_session is None:
            self._init_request_session(proxy_uri)
        requests_args = {'timeout': (10.0, 5.0), 'verify': verify}
        if parameters:
            requests_args['params'] = parameters
        if payload:
            if isinstance(payload, (dict, list)):
                requests_args['json'] = payload
            else:
                requests_args['data'] = str(payload)
        if headers:
            requests_args['headers'] = headers
        if cookies:
            requests_args['cookies'] = cookies
        if cert:
            requests_args['cert'] = cert
        if timeout is not None:
            requests_args['timeout'] = timeout
        if self.requests_proxy:
            requests_args['proxies'] = self.requests_proxy
            if self.logger:
                safe_proxy = str(self.requests_proxy).split('@')[-1] if '@' in str(self.requests_proxy) else str(self.requests_proxy)
                self.logger.debug('Making {0} request to {1} via proxy'.format(method, url))
        return self.http_session.request(method, url, **requests_args)
