# -*- coding: utf-8 -*-
import os
import os.path
import datetime
import json
import requests
import requests.exceptions

from . import sitecfg


class EveCentral:
    def __init__(self, config: sitecfg.SiteConfig):
        self.api_url_base = 'http://api.eve-central.com/api/'
        self._cache_dir = config.EVECENTRAL_CACHE_DIR
        self._cache_time = config.EVECENTRAL_CACHE_HOURS * 3600
        self._debug = False
        # solarsystem IDs
        self.JITA_ID = 30000142
        self.AMARR_ID = 30002187
        self.DODIXIE_ID = 30002659
        self.HEK_ID = 30002053
        self.RENS_ID = 30002510
        self.FULLERITE_C320 = 30377
        # HTTP headers
        self._headers = dict()
        self._headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self._headers['accept-language'] = 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
        self._headers['accept-encoding'] = 'gzip, deflate'
        self._headers['user-agent'] = 'WHDBX/EVE-Central agent, alexey.min@gmail.com'

    def _load_cache_file(self, cache_file: str, ignore_time: bool=False) -> str:
        ret = ''
        if os.path.isfile(cache_file) and os.access(cache_file, os.R_OK):
            # check if cache file is too old for now
            # get file modification time
            st = os.stat(cache_file)
            dt_cache = datetime.datetime.fromtimestamp(st.st_mtime)
            # get current time
            dt_now = datetime.datetime.now()
            # compare deltas
            delta = dt_now - dt_cache
            delta_secs = delta.total_seconds()
            if (delta_secs < self._cache_time) or (ignore_time is True):
                if self._debug:
                    print('EveCentral: Loading from cache file: [{0}]'.format(cache_file))
                try:
                    f = open(cache_file, 'rt')
                    ret = f.read()
                    f.close()
                except IOError as e:
                    if self._debug:
                        print('EveCentral: failed to read cache data from file: [{0}]'.format(cache_file))
                        print(str(e))
            else:
                if self._debug:
                    print('EveCentral: Cache file [{0}] skipped, too old: {1} secs. (limit was: {2})'.
                          format(cache_file, delta_secs, self._cache_time))
                # Do not delete cache file, it will be just overwritten
                #  in case of successful request, or left to live otherwise
                #  this will allow to get at least any old data in the case of failure
                # os.remove(cache_file)
        return ret

    def _save_to_cache_file(self, cache_file: str, data: str):
        # auto-create cache dir if not exists
        if not os.path.isdir(self._cache_dir):
            try:
                os.makedirs(self._cache_dir)
            except OSError:
                pass
        try:
            f = open(cache_file, 'wt')  # probably may overwrite old cached file for this request
            f.write(data)
            f.close()
        except IOError as e:
            if self._debug:
                print("EveCentral: Can't store reply to cache file [{0}]:".format(cache_file))
                print(str(e))

    def _load_price_from_cache(self, typeid: int, solarsystem: int, ignore_time: bool=False) -> str:
        ret = ''
        if typeid < 0:
            return ret
        cache_file = self._cache_dir + '/' + str(typeid) + '_' + str(solarsystem) + '.json'
        return self._load_cache_file(cache_file, ignore_time)

    def _save_price_to_cache(self, data: str, typeid: int, solarsystem: int):
        if typeid < 0:
            return
        cache_file = self._cache_dir + '/' + str(typeid) + '_' + str(solarsystem) + '.json'
        self._save_to_cache_file(cache_file, data)

    def _load_url(self, url: str) -> str:
        ret = ''
        try:
            if self._debug:
                print('EveCentral: Sending request! {0}'.format(url))
            r = requests.get(url, headers=self._headers)
            if r.status_code == 200:
                ret = r.text
            else:
                if self._debug:
                    print('EveCentral: ERROR: HTTP response code: {0}'.format(r.status_code))
        except requests.exceptions.RequestException as e:
            if self._debug:
                print(str(e))
        return ret

    def _load_price_from_web(self, typeid: int, solarsystem: int) -> str:
        url = self.api_url_base + 'marketstat/json?typeid='
        url += str(typeid)
        if solarsystem > 0:
            url += '&usesystem=' + str(solarsystem)
        return self._load_url(url)

    def marketstat(self, typeid: int, solarsystem: int=0, ignore_time: bool=False):
        ret = self._load_price_from_cache(typeid, solarsystem)
        if ret == '':
            ret = self._load_price_from_web(typeid, solarsystem)
            if ret != '':  # request succeeded
                self._save_price_to_cache(ret, typeid, solarsystem)
            if ret == '':  # request failed :(
                if ignore_time:  # try to load old, outdated price data from cache anyway
                    ret = self._load_price_from_cache(typeid, solarsystem, True)
        if ret != '':
            ret = json.loads(ret)
        else:
            ret = None
        return ret

    def sell_min(self, typeid: int, solarsystem: int=0, ignore_time: bool=False) -> float:
        ret = self.marketstat(typeid, solarsystem, ignore_time)
        if not ret:
            return 0.0
        if type(ret) == list:
            if type(ret[0]) == dict:
                return float(ret[0]['sell']['min'])
        return 0.0

    def buy_max(self, typeid: int, solarsystem: int=0, ignore_time: bool=False) -> float:
        ret = self.marketstat(typeid, solarsystem, ignore_time)
        if not ret:
            return 0.0
        if type(ret) == list:
            if type(ret[0]) == dict:
                return float(ret[0]['buy']['max'])
        return 0.0

    def Jita_sell_min(self, typeid: int, ignore_time: bool=False) -> float:
        return self.sell_min(typeid, self.JITA_ID, ignore_time)

    def Jita_buy_max(self, typeid: int, ignore_time: bool=False) -> float:
        return self.buy_max(typeid, self.JITA_ID, ignore_time)

    def route(self, from_ss: str, to_ss: str) -> list:
        # cache filename
        cache_file = self._cache_dir + '/' + 'route_from_'
        cache_file += from_ss
        cache_file += '_to_'
        cache_file += to_ss
        cache_file += '.json'
        # try to load from cache
        ret = self._load_cache_file(cache_file, True)  # ignoring time
        if ret != '':
            return json.loads(ret)
        # if we are here, cache has no this file
        if self._debug:
            print('EveCentral: route: [{0}->{1}] requesting web...'.format(from_ss, to_ss))
        # http://api.eve-central.com/api/route/from/Jita/to/V2-VC2
        url = self.api_url_base + 'route/from/'
        url += str(from_ss)
        url += '/to/'
        url += str(to_ss)
        ret = self._load_url(url)
        if ret != '':
            self._save_to_cache_file(cache_file, ret)
            return json.loads(ret)
        # if we are here, HTTP request failed =(
        return list()

#  Only Jita: http://api.eve-central.com/api/marketstat/json?typeid=30377&usesystem=30000142
#  All systems: http://api.eve-central.com/api/marketstat/json?typeid=30377

#  ret2 = ec.marketstat(30377, ec.JITA_ID)
#  >>> ret2[0]['sell']['min']
#  70998.97
#  >>> ret2[0]['buy']['max']
#  65504.57

"""[
    {
        "buy":
        {
            "forQuery":
            {
                "bid":true,
                "types":[30377],
                "regions":[],
                "systems":[30000142],
                "hours":24,
                "minq":1
            },
            "volume":551491,
            "wavg":47420.5817246519,
            "avg":50736.196153846155,
            "variance":2.9294287243929297E8,
            "stdDev":17115.57397341068,
            "median":45100.02,
            "fivePercent":65504.47090909091,
            "max":65504.48,
            "min":21499.0,
            "highToLow":true,
            "generated":1426598383990
        },

        "all":
        {
            "forQuery":
            {
                "bid":null,
                "types":[30377],
                "regions":[],
                "systems":[30000142],
                "hours":24,
                "minq":1
            },
            "volume":1162961,
            "wavg":50019.75256822027,
            "avg":68492.25819277109,
            "variance":4.304307935530102E8,
            "stdDev":20746.826107937817,
            "median":52003.0,
            "fivePercent":101.0,
            "max":120000.0,
            "min":101.0,
            "highToLow":false,
            "generated":1426598383990
        },

        "sell":
        {
            "forQuery":
            {
                "bid":false,
                "types":[30377],
                "regions":[],
                "systems":[30000142],
                "hours":24,
                "minq":1
            },
            "volume":400359,
            "wavg":79919.68235903277,
            "avg":79372.80600000001,
            "variance":7.358930295783491E7,
            "stdDev":8578.420772953197,
            "median":77488.98,
            "fivePercent":70999.95793511528,
            "max":120000.0,
            "min":70999.0,
            "highToLow":false,
            "generated":1426598383991
        }
    }
]
"""

# http://api.eve-central.com/api/route/from/Jita/to/V2-VC2
# [{
#   "from": {
#      "systemid":30000142,
#      "name":"Jita",
#      "security":0.9,
#      "region": {
#         "regionid":10000002,
#         "name":"The Forge"
#      },
#      "constellationid":20000020
#   },
#   "to": {
#     "systemid":30000144,
#     "name":"Perimeter",
#     "security":1.0,
#     "region": {
#       "regionid":10000002,
#       "name":"The Forge"
#     },
#     "constellationid":20000020
#   },
#  "secChange":false},
#  ..., ... ]