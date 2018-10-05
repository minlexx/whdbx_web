# -*- coding: utf-8 -*-
import os
import os.path
import datetime
import json
import sqlite3

# Uses python-requests
# http://docs.python-requests.org/en/latest/
import requests
import requests.exceptions

# Look at the X-Bin-Request-Count header and X-Bin-Max-Requests header
# for how many requests you've made, and how many you can make pr. hour.
# You can do any amount of requests pr. second that you want.

# All IDs used with the API are CCP IDs (Except killmail IDs, which can be
# internally set, but they are denoted with a - infront (negative numbers))

# If you get an error 403, look at the Retry-After header.

# The API will maximum deliver of 200 killmails.

# Up to 10 IDs can be fetched at the same time, by seperating them with a , (Comma)

# All modifiers can be combined in any order


# Examples of options both for ZKB class and cache classes:
zkb_cache_options_file = {
    'debug': True,
    'cache_time': 1200,
    'cache_type': 'file',
    'cache_dir': './_caches/zkb',
    'use_evekill': True
}

zkb_cache_options_sqlite = {
    'debug': True,
    'cache_time': 1200,
    'cache_type': 'sqlite',
    'cache_file': './_caches/zkb/zkb_cache.db',
    'use_evekill': True
}


class ZKBCacheBase:
    def __init__(self, options: dict=None):
        self._cache_time = 600  # seconds
        self._debug = False
        if options:
            if 'cache_time' in options:
                self._cache_time = int(options['cache_time'])
            if 'debug' in options:
                self._debug = options['debug']

    def get_json(self, request_str: str):
        return None

    def save_json(self, request_str: str, reply_str: str):
        return None


class ZKBCacheFile(ZKBCacheBase):
    def __init__(self, options: dict=None):
        super(ZKBCacheFile, self).__init__(options)
        self._cache_dir = None
        if options:
            if 'cache_dir' in options:
                cache_dir = options['cache_dir']
                # create dir if it does not exist
                if not os.access(cache_dir, os.R_OK):
                    os.makedirs(cache_dir, exist_ok=True)
                else:
                    if not os.path.isdir(cache_dir):
                        # already exists and is not a directory
                        raise IOError('ZKBCacheFile: Already exists and is NOT a directory: ' + cache_dir)
                self._cache_dir = cache_dir

    def get_json(self, request_str: str):
        ret = ''
        if request_str is None:
            return ret
        if self._cache_dir is None:
            return ret
        cache_file = self._cache_dir + '/' + request_str + '.json'
        # first try to get from cache
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
            if delta_secs < self._cache_time:
                if self._debug:
                    print('ZKBCacheFile: Loading from cache: [{0}]'.format(cache_file))
                try:
                    f = open(cache_file, 'rt')
                    ret = f.read()
                    f.close()
                except IOError as e:
                    if self._debug:
                        print('ZKBCacheFile: failed to read cache data from: [{0}]'.format(cache_file))
                        print(str(e))
            else:
                if self._debug:
                    print('ZKBCacheFile: Cache file [{0}] skipped, too old: {1} secs. (limit was: {2})'.
                          format(cache_file, delta_secs, self._cache_time))
                # Do not delete cache file, it will be just overwritten
                #  in case of successful request, or left to live otherwise
                #  this will allow to get at least any old data in the case of failure
                # Or maybe delete it anyway?...
                os.remove(cache_file)
        return ret

    def save_json(self, request_str: str, reply_str: str):
        if request_str is None:
            return
        if reply_str is None:
            return
        if self._cache_dir is None:
            return
        # auto-create cache dir if not exists
        if not os.path.isdir(self._cache_dir):
            try:
                os.makedirs(self._cache_dir)
            except OSError:
                pass
        cache_file = self._cache_dir + '/' + request_str + '.json'
        # store reply to cache file
        try:
            f = open(cache_file, 'wt')  # probably may overwrite old cached file for this request
            f.write(reply_str)
            f.close()
        except IOError as e:
            if self._debug:
                print("ZKBCacheFile: Can't store reply to cache file:")
                print(str(e))


class ZKBCacheSqlite(ZKBCacheBase):
    def __init__(self, options: dict=None):
        super(ZKBCacheSqlite, self).__init__(options)
        self._cache_file = None
        self._db = None
        if options:
            if 'cache_file' in options:
                self._cache_file = options['cache_file']
                if (self._cache_file is not None) and (self._cache_file != ''):
                    self._db = sqlite3.connect(self._cache_file)
                    cur = self._db.cursor()
                    cur.execute('CREATE TABLE IF NOT EXISTS zkb_cache '
                                '(req text, resp text, save_time int)')
                    self._db.commit()
                    cur.close()

    def get_json(self, request_str: str):
        ret = ''
        if not self._cache_file:
            return ret
        if not self._db:
            return ret
        tm_now = int(datetime.datetime.now().timestamp())
        cur = self._db.cursor()
        cur.execute('SELECT resp, save_time FROM zkb_cache WHERE req = ?', (request_str,))
        row = cur.fetchone()
        if row:
            save_time = int(row[1])
            time_passed = tm_now - save_time
            if time_passed > self._cache_time:
                cur.close()
                # delete old record
                cur = self._db.cursor()
                cur.execute('DELETE FROM zkb_cache WHERE req = ? AND save_time = ?', (request_str, save_time))
                self._db.commit()
            else:
                ret = row[0]
        cur.close()
        return ret

    def save_json(self, request_str: str, reply_str: str):
        if not self._cache_file:
            return
        if not self._db:
            return
        tm_now = int(datetime.datetime.now().timestamp())
        cur = self._db.cursor()
        cur.execute('INSERT INTO zkb_cache (req, resp, save_time) VALUES (?, ?, ?)',
                    (request_str, reply_str, tm_now))
        self._db.commit()
        cur.close()
        return


class ZKB:
    def __init__(self, options: dict=None):
        self.HOURS = 3600
        self.DAYS = 24 * self.HOURS
        self._BASE_URL_ZKB = 'https://zkillboard.com/api/'
        self._BASE_URL_EVEKILL = 'https://beta.eve-kill.net/api/combined/'
        self._headers = dict()
        self._headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self._headers['accept-language'] = 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
        self._headers['accept-encoding'] = 'gzip, deflate'
        self._headers['user-agent'] = 'Python/ZKB agent, alexey.min@gmail.com'
        self._url = ''
        self._modifiers = ''
        self._cache = None
        self._debug = False
        self._use_evekill = False
        self.request_count = 0
        self.max_requests = 0
        self.kills_on_page = 0
        self.clear_url()
        # parse options
        if options:
            if 'debug' in options:
                self._debug = options['debug']
            if 'user_agent' in options:
                self._headers['user-agent'] = options['user_agent']
            if 'use_evekill' in options:
                self._use_evekill = options['use_evekill']
                self.clear_url()
            if 'cache_type' in options:
                cache_type = options['cache_type']
                if cache_type == 'file':
                    self._cache = ZKBCacheFile(options)
                elif cache_type == 'sqlite':
                    self._cache = ZKBCacheSqlite(options)
                else:
                    raise IndexError('ZKB: Unknown cache_type in options: ' + cache_type)
            if 'kills_on_page' in options:
                self.kills_on_page = options['kills_on_page']

    def clear_url(self):
        self._url = self._BASE_URL_ZKB
        if self._use_evekill:
            self._url = self._BASE_URL_EVEKILL
        self._modifiers = ''

    def add_modifier(self, mname, mvalue=None):
        self._url += mname
        self._url += '/'
        self._modifiers += mname
        self._modifiers += '_'
        if mvalue:
            self._url += str(mvalue)
            self._url += '/'
            self._modifiers += str(mvalue)
            self._modifiers += '_'

    # startTime and endTime is datetime timestamps, in the format YmdHi..
    #  Example 2012-11-25 19:00 is written as 201211251900
    def add_startTime(self, st=datetime.datetime.now()):
        self.add_modifier('startTime', st.strftime('%Y%m%d%H%M'))

    # startTime and endTime is datetime timestamps, in the format YmdHi..
    #  Example 2012-11-25 19:00 is written as 201211251900
    def add_endTime(self, et=datetime.datetime.now()):
        self.add_modifier('endTime', et.strftime('%Y%m%d%H%M'))

    #  pastSeconds returns only kills that have happened in the past x seconds.
    #  pastSeconds can maximum go up to 7 days (604800 seconds)
    def add_pastSeconds(self, s):
        self.add_modifier('pastSeconds', s)

    def add_year(self, y):
        self.add_modifier('year', y)

    def add_month(self, m):
        self.add_modifier('month', m)

    def add_week(self, w):
        self.add_modifier('week', w)

    # If the /limit/ modifier is used, then /page/ is unavailable.
    def add_limit(self, limit):
        self.add_modifier('limit', str(limit))

    # Page reqs over 10 are only allowed for characterID, corporationID and allianceID
    def add_page(self, page):
        self.add_modifier('page', page)

    def add_beforeKillID(self, killID):
        self.add_modifier('beforeKillID', killID)

    def add_afterKillID(self, killID):
        self.add_modifier('afterKillID', killID)

    # To get combined /kills/ and /losses/, don't pass either /kills/ or /losses/
    def add_kills(self):
        self.add_modifier('kills')

    # To get combined /kills/ and /losses/, don't pass either /kills/ or /losses/
    def add_losses(self):
        self.add_modifier('losses')

    #  /w-space/ and /solo/ can be combined with /kills/ and /losses/
    def add_wspace(self):
        self.add_modifier('w-space')

    #  /w-space/ and /solo/ can be combined with /kills/ and /losses/
    def add_solo(self):
        self.add_modifier('solo')

    # If you do not paass /killID/ then you must pass at least two
    #  of the following modifiers. /w-space/, /solo/ or any of the /xID/ ones.
    #  (characterID, allianceID, factionID etc.)
    def add_killID(self, killID):
        self.add_modifier('killID', killID)

    def add_orderAsc(self):
        self.add_modifier('orderDirection', 'asc')

    def add_orderDesc(self):
        self.add_modifier('orderDirection', 'desc')

    def add_noItems(self):
        self.add_modifier('no-items')

    def add_noAttackers(self):
        self.add_modifier('no-attackers')

    def add_character(self, charID):
        self.add_modifier('characterID', charID)

    def add_corporation(self, corpID):
        self.add_modifier('corporationID', corpID)

    def add_alliance(self, allyID):
        self.add_modifier('allianceID', allyID)

    def add_faction(self, factionID):
        self.add_modifier('factionID', factionID)

    def add_shipType(self, shipTypeID):
        self.add_modifier('shipTypeID', shipTypeID)

    def add_group(self, groupID):
        self.add_modifier('groupID', groupID)

    def add_solarSystem(self, solarSystemID):
        self.add_modifier('solarSystemID', solarSystemID)

    # Default cache lifetime set to 1 hour (3600 seconds)
    def go(self):
        zkb_kills = []
        ret = ''
        # first, try to get from cache
        if self._cache:
            ret = self._cache.get_json(self._modifiers)
        if (ret is None) or (ret == ''):
            # either no cache exists or cache read error :( send request
            try:
                if self._debug:
                    print('ZKB: Sending request! {0}'.format(self._url))
                r = requests.get(self._url, headers=self._headers)
                if r.status_code == 200:
                    ret = r.text
                    if 'x-bin-request-count' in r.headers:
                        self.request_count = int(r.headers['x-bin-request-count'])
                    if 'x-bin-max-requests' in r.headers:
                        self.max_requests = int(r.headers['x-bin-max-requests'])
                    if self._debug:
                        print('ZKB: We are making {0} requests of {1} allowed per hour.'.
                              format(self.request_count, self.max_requests))
                elif r.status_code == 403:
                    # If you get an error 403, look at the Retry-After header.
                    retry_after = r.headers['retry-after']
                    if self._debug:
                        print('ZKB: ERROR: we got 403, retry-after: {0}'.format(retry_after))
                else:
                    if self._debug:
                        print('ZKB: ERROR: HTTP response code: {0}'.format(r.status_code))
            except requests.exceptions.RequestException as e:
                if self._debug:
                    print(str(e))
            # request done, see if we have a response
            if ret != '':
                if self._cache:
                    self._cache.save_json(self._modifiers, ret)
        # parse response JSON, if we have one
        if (ret is not None) and (ret != ''):
            zkb_kills = []
            try:
                zkb_kills = json.loads(ret)
            except ValueError:
                # skip JSON parse errors
                pass
            utcnow = datetime.datetime.utcnow()
            try:
                if self.kills_on_page > 0:
                    # manually limit number of kills to process
                    zkb_kills = zkb_kills[0:self.kills_on_page]
                for a_kill in zkb_kills:
                    # a_kill should be a dict object.
                    # Sometimes ZKB can return 'error' key as string, we can parse only dicts
                    if type(a_kill) != dict:
                        continue

                    # kill price in ISK, killmail hash
                    a_kill['killmail_hash'] = ''
                    a_kill['total_value'] = 0
                    a_kill['total_value_m'] = 0
                    a_kill['is_npc'] = False
                    a_kill['is_solo'] = False
                    if 'zkb' in a_kill:
                        if 'totalValue' in a_kill['zkb']:
                            a_kill['total_value'] = float(a_kill['zkb']['totalValue'])
                            a_kill['total_value_m'] = round(float(a_kill['zkb']['totalValue']) / 1000000.0)
                        if 'hash' in a_kill['zkb']:
                            a_kill['killmail_hash'] = a_kill['zkb']['hash']
                        if 'npc' in a_kill['zkb']:
                            a_kill['is_npc'] = a_kill['zkb']['npc']
                        if 'solo' in a_kill['zkb']:
                            a_kill['is_solo'] = a_kill['zkb']['solo']
                    del a_kill['zkb']
            except KeyError as k_e:
                if self._debug:
                    print('It is possible that ZKB API has changed (again).')
                    print(str(k_e))
        return zkb_kills

# #################################
# Unimplemented / Unused:
#  /api-only/
#  /xml/

# https://zkillboard.com/system/31000707/


def pretty_print_kill(kill):
    for k in kill.keys():
        print('kill[{0}] -> {1}'.format(str(k), str(kill[k])))
# kill[killmail_id] -> 72725284
# kill[zkb] -> {
#    'locationID': 40387568,
#    'hash': '56a83bf9445ad4ed88426b19e600e801e6ab57f4',
#    'fittedValue': 1320489.39,
#    'totalValue': 48235664.21,
#    'points': 1,
#    'npc': False,
#    'solo': True,
#    'awox': False
# }


if __name__ == '__main__':
    zkb_options_file = {
        'debug': True,
        'cache_time': 1200,
        'cache_type': 'file',
        'cache_dir': './_caches/zkb',
        'use_evekill': False
    }
    zkb_options_sqlite = {
        'debug': True,
        'cache_time': 1200,
        'cache_type': 'sqlite',
        'cache_file': './_caches/zkb/zkb_cache.db',
        'use_evekill': False
    }
    z = ZKB(zkb_options_file)
    # z = ZKB(zkb_options_sqlite)
    z.add_solarSystem('31000707')
    # z.add_limit(1)  # no more limits
    zkb_kills = z.go()
    if len(zkb_kills) > 0:
        i = 0
        for a_kill in zkb_kills:
            if i == 0:
                pretty_print_kill(a_kill)
            i += 1