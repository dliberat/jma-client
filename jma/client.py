"""Download daily irradiation data from the Japanese Meteorological Association
(https://www.data.jma.go.jp/gmd/risk/obsdl/index.php).
"""
from datetime import datetime
import logging
import requests

from jma.exceptions import JmaException, NoSessionIdException, BadCsvException
from jma.jmastation import JmaStation
from jma.response import JmaIrradiationResponse, JmaHourlyIrradiationResponse

logger = logging.getLogger('jmaclient')


class JmaClient():

    TIMEOUT = 3 # seconds

    def __init__(self, kwh=False):
        """
        Args:
            kwh (bool) - If true, values will be converted from MJ/m2 to kWh/m2
        """
        self.sess = None
        self.php_sessid = None
        self.kwh = kwh

    def __enter__(self):
        self.sess = requests.Session()
        res = self._get('https://www.data.jma.go.jp/gmd/risk/obsdl/index.php')
        res.raise_for_status()
        self.php_sessid = extract_php_sessid(res.text)
        return self

    def __exit__(self, a, b, c):
        pass

    def _get(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.TIMEOUT
        return self.sess.get(*args, **kwargs)
    
    def _post(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.TIMEOUT
        return self.sess.post(*args, **kwargs)

    def _send_request(self, params):
        uri = 'https://www.data.jma.go.jp/gmd/risk/obsdl/show/table.html'
        hdr = {
            'Host':               'www.data.jma.go.jp',
            'User-Agent':         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0',
            'Accept':             'text/html, */*; q=0.01',
            'Accept-Language':    'en-US,en;q=0.5',
            'Accept-Encoding':    'gzip, deflate, br',
            'Content-Type':       'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin':             'https://www.data.jma.go.jp',
            'DNT':                '1',
            'Connection':         'keep-alive',
            'Referer':            'https://www.data.jma.go.jp/gmd/risk/obsdl/index.php',
        }
        
        res = self._post(uri, data=params, headers=hdr)
        try:
            res.raise_for_status()
            raise_if_html(res.text)
        except requests.exceptions.HTTPError:
            logger.exception(f'POST request failed. Request body: {res.request.body}')
            raise JmaException('Request failed')
        except BadCsvException:
            logger.exception(f'POST request failed. Request body: {res.request.body}')
            raise
        res.encoding = 'shift-jis'
        return res

    def get_daily_irradiation(self, start_date, end_date, stations, lta=False):
        """Download irradiation data in increments of 1 day.
        Args:
            start_date (datetime.date) - First date for which irradiation data will be downloaded
            end_date (datetime.date) - Last date (inclusive) for which irradiation data will be downloaded
            stations (List[JmaStation]) - Iterable of JmaStation
            lta (bool) - True if long-term average irradation should be included in results
        Returns:
            JmaIrradiationResponse
        """
        date_arr = [
            start_date.year,
            end_date.year,
            start_date.month,
            end_date.month,
            start_date.day,
            end_date.day,
        ]
        opts = '[["op1",0]]' if lta else []
        params = {
            'stationNumList':       encode_list_for_jma([stn.value for stn in stations]),
            'aggrgPeriod':          1,
            'elementNumList':       '[["610",""]]',
            'interAnnualFlag':      1,
            'ymdList':             	encode_list_for_jma(date_arr),
            'optionNumList':        opts,
            'downloadFlag':         True,
            'rmkFlag':              0,
            'disconnectFlag':       0,
            'youbiFlag':            0,
            'fukenFlag':            0,
            'kijiFlag':             0,
            'huukouFlag':           0,
            'csvFlag':              0,
            'jikantaiFlag':         0,
            'jikantaiList':         [],
            'ymdLiteral':           1,
            'PHPSESSID':            self.php_sessid,
        }
        res = self._send_request(params)
        return JmaIrradiationResponse(res.text, kwh=self.kwh)

    def get_hourly_irradiation(self, start_date, end_date, stations, lta=False):
        """Download irradiation data in increments of 1 hour.
        Args:
            start_date (datetime.date) - First date for which irradiation data will be downloaded
            end_date (datetime.date) - Last date (inclusive) for which irradiation data will be downloaded
            stations (List[JmaStation]) - Iterable of JmaStation
            lta (bool) - True if long-term average irradation should be included in results
        Returns:
            JmaIrradiationResponse
        """
        date_arr = [
            start_date.year,
            end_date.year,
            start_date.month,
            end_date.month,
            start_date.day,
            end_date.day,
        ]
        opts = '[["op1",0]]' if lta else []
        params = {
            'stationNumList':       encode_list_for_jma([stn.value for stn in stations]),
            'aggrgPeriod':          9,
            'elementNumList':       '[["610",""]]',
            'interAnnualFlag':      1,
            'ymdList':             	encode_list_for_jma(date_arr),
            'optionNumList':        opts,
            'downloadFlag':         True,
            'rmkFlag':              0,
            'disconnectFlag':       0,
            'youbiFlag':            0,
            'fukenFlag':            0,
            'kijiFlag':             0,
            'huukouFlag':           0,
            'csvFlag':              0,
            'jikantaiFlag':         0,
            'jikantaiList':         '[1,24]',
            'ymdLiteral':           1,
            'PHPSESSID':            self.php_sessid,
        }
        res = self._send_request(params)
        return JmaHourlyIrradiationResponse(res.text, kwh=self.kwh)


def encode_list_for_jma(seq) -> str:
    return '[' + ','.join([f'"{c}"' for c in seq]) + ']'


def extract_php_sessid(html: str):
    """JMA stores its PHP Session ID in a tag with the form:
    <input type="hidden" id="sid" value="xxx" />

    Args:
        html (str) - HTML content of the JMA data download page
    
    Returns:
        str - value of the PHP Session ID
    """
    try:
        search = '<input type="hidden" id="sid" value="'
        search_len = len(search)
        s = html.index(search) + search_len
        e = html.index('"', s+2)
        return html[s:e] # everything between the quotation marks 
    except ValueError:
        logger.exception(html)
        raise NoSessionIdException('Cannot locate PHP Session ID')


def raise_if_html(text: str):
    if '<head>' in text or '<body' in text:
        raise BadCsvException('Is HTML page')
