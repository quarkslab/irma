import sys
import logging

log = logging.getLogger(__name__)


# =====
#  Api
# =====

class VirusTotal(object):

    # =========
    #  Helpers
    # =========

    @staticmethod
    def get_response(url, method="get", **kwargs):
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

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, api_key, **kwargs):
        # late import to avoid dependencies
        global requests
        import requests
        # initialize internals
        self.api_key = api_key
        self.api_url = 'https://www.virustotal.com/vtapi/v2/'

    # ==================
    #  Internal methods
    # ==================

    def get_report(self, hashval):
        params = {'resource': hashval, 'apikey': self.api_key}
        url = '{base}{path}'.format(base=self.api_url, path='file/report')
        jdata, _ = VirusTotal.get_response(url, params=params)
        return jdata
