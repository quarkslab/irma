from lib.common.hash import sha256sum

##############################################################################
# api
##############################################################################

class VirusTotal(object):

    ##########################################################################
    # helpers
    ##########################################################################

    @staticmethod
    def get_response(url, method = "get", **kwargs):
        jdata, response = '', ''
        while True:
            try:
                response = getattr(requests, method)(url, **kwargs)
            except requests.exceptions.ConnectionError as e:
                log.exception(e)
                sys.exit(1)
            if response.status_code != 204:
                try:
                    jdata = response.json()
                except:
                    jdata = response.json
                break
        return jdata, response

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        # initialize internals
        self.api_key = kwargs.get('api_key', None)
        self.api_url = 'https://www.virustotal.com/vtapi/v2/'

    ##########################################################################
    # internal methods
    ##########################################################################

    def get_report(self, hash):
        params = { 'resource': hash, 'apikey': self.api_key }
        url = '{base}{path}'.format(base = self.api_url, path = 'file/report')
        jdata, response = VirusTotal.get_response(url, params = params)
        return jdata

    ##########################################################################
    # overriden methods
    ##########################################################################

    # TODO: remove overriden methods

    def scan(self, paths):
        sha256 = sha256sum(paths)
        return self.get_report(sha256)

    def ready(self):
        result = False
        try:
            import requests
            global requests
            if self.api_key:
                result = True
        except ImportError as e:
            pass
        return result
