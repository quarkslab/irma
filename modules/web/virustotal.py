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

    def __init__(self, api_key, **kwargs):
        # late import to avoid dependencies
        global requests
        import requests
        # initialize internals
        self.api_key = api_key
        self.api_url = 'https://www.virustotal.com/vtapi/v2/'

    ##########################################################################
    # internal methods
    ##########################################################################

    def get_report(self, hash):
        params = { 'resource': hash, 'apikey': self.api_key }
        url = '{base}{path}'.format(base = self.api_url, path = 'file/report')
        jdata, response = VirusTotal.get_response(url, params = params)
        return jdata
