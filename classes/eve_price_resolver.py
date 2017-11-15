# -*- coding: utf-8 -*-
import os
import os.path
import datetime
import json
import requests
import requests.exceptions

from . import sitecfg
from . import esi_calls


class EvePriceResolver:
    """
    Base class for all price resolve methods available
    """

    # solarsystem IDs
    JITA_SSID = 30000142
    AMARR_SSID = 30002187
    DODIXIE_SSID = 30002659
    HEK_SSID = 30002053
    RENS_SSID = 30002510
    # region IDs
    THE_FORGE_REGIONID = 10000002
    DOMAIN_REGIONID = 10000043
    SINQ_LAISON_REGIONID = 10000032
    METROPOLIS_REGIONID = 10000042
    # station IDs
    JITA4_MOON4_STATIONID = 60003760
    # gas IDs
    FULLERITE_C320_TYPEID = 30377

    def Jita_sell_min(self, typeid: int, ignore_time: bool=False) -> float:
        return 0.0

    def Jita_buy_max(self, typeid: int, ignore_time: bool=False) -> float:
        return 0.0


class EveCentralPriceResolver(EvePriceResolver):
    def __init__(self, config: sitecfg.SiteConfig):
        self.api_url_base = 'http://api.eve-central.com/api/'
        self._cache_dir = config.EVECENTRAL_CACHE_DIR
        self._cache_time = config.EVECENTRAL_CACHE_HOURS * 3600
        self._debug = config.DEBUG
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
        contents = ''
        if typeid < 0:
            return contents
        cache_file = self._cache_dir + '/' + str(typeid) + '_' + str(solarsystem) + '.json'
        contents = self._load_cache_file(cache_file, ignore_time)
        # test that string loaded from file is a valid JSON
        # only if file shoudl be loaded anyways, independently of time
        if ignore_time:
            try:
                json.loads(contents)
            except json.JSONDecodeError:
                # not a valid JSON, return empty string and delete an invalid cached file
                if self._debug:
                    print('EveCentral: cache file "{}" does not contain a valid JSON and '
                          'ignore_time is set, it will be removed.'.format(cache_file))
                contents = ''
                try:
                    os.remove(cache_file)
                except IOError:
                    pass
        return contents

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
        contents = self._load_url(url)
        # Eve-Central: test that returned result is a valid JSON, skip invalid replies
        try:
            json.loads(contents)
        except json.JSONDecodeError:
            contents = ''  # not a valid JSON, looks like an error with EVE-Central
            if self._debug:
                print('EveCentral: Loading price from eve-central failed, not a valid JSON!')
        return contents

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

    def marketstat_sell_min(self, typeid: int, solarsystem: int=0, ignore_time: bool=False) -> float:
        ret = self.marketstat(typeid, solarsystem, ignore_time)
        if not ret:
            return 0.0
        if type(ret) == list:
            if type(ret[0]) == dict:
                return float(ret[0]['sell']['min'])
        return 0.0

    def marketstat_buy_max(self, typeid: int, solarsystem: int=0, ignore_time: bool=False) -> float:
        ret = self.marketstat(typeid, solarsystem, ignore_time)
        if not ret:
            return 0.0
        if type(ret) == list:
            if type(ret[0]) == dict:
                return float(ret[0]['buy']['max'])
        return 0.0

    def Jita_sell_min(self, typeid: int, ignore_time: bool=False) -> float:
        return self.marketstat_sell_min(typeid, self.JITA_SSID, ignore_time)

    def Jita_buy_max(self, typeid: int, ignore_time: bool=False) -> float:
        return self.marketstat_buy_max(typeid, self.JITA_SSID, ignore_time)


class EsiPriceResolver(EvePriceResolver):
    def __init__(self, cfg: sitecfg.SiteConfig):
        self._cfg = cfg
        self._cache_dir = cfg.EVECENTRAL_CACHE_DIR
        self._cache_time = cfg.EVECENTRAL_CACHE_HOURS * 3600
        self._debug = cfg.DEBUG

    def Jita_sell_min(self, typeid: int, ignore_time: bool=False) -> float:
        orders = esi_calls.market_region_orders(self._cfg, self.THE_FORGE_REGIONID, 'sell', typeid)
        if len(orders) < 1:
            return 0.0
        min_price = orders[0]['price']
        for order in orders:
            cur_price = order['price']
            if cur_price < min_price:
                min_price = cur_price
        return min_price

    def Jita_buy_max(self, typeid: int, ignore_time: bool=False) -> float:
        orders = esi_calls.market_region_orders(self._cfg, self.THE_FORGE_REGIONID, 'buy', typeid)
        if len(orders) < 1:
            return 0.0
        max_price = orders[0]['price']
        for order in orders:
            cur_price = order['price']
            if cur_price > max_price:
                max_price = cur_price
        return max_price



def get_resolver(cfg: sitecfg.SiteConfig) -> EvePriceResolver:
    """
    Factory method to get a proper configured price resolver class
    :param cfg: site config, whose PRICE_RESOLVER field is used to determine a resolver
    :return: correct price resolver class, or raise ValueError on invalid input.
    """
    if cfg.PRICE_RESOLVER == 'evecentral':
        ret = EveCentralPriceResolver(cfg)
        return ret
    if cfg.PRICE_RESOLVER == 'esi':
        ret = EsiPriceResolver(cfg)
        return ret
    raise ValueError('resolver_factory: unknown PRICE_RESOLVER set in whdbx_config.ini: {};'
                     ' use one of "esi", "evecentral"'.format(cfg.PRICE_RESOLVER))
