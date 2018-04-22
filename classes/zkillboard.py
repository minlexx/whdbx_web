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
                    # fix new keys format to old format, becuase templates use old keys
                    a_kill['killID'] = a_kill['killmail_id']
                    # init a kill datetime with an empty date
                    a_kill['kill_dt'] = datetime.datetime(1970, 1, 1, 0, 0, 0)
                    a_kill['killTime'] = a_kill['killmail_time']  # compatibility with old API
                    # guess time format, ZKB has changed it over time
                    # ValueError: time data '2015.07.08 01:11:00' does not match format '%Y-%m-%d %H:%M:%S'
                    # current ZKB has a totallly different time format: "2017-06-07T17:02:57Z"
                    try:
                        a_kill['kill_dt'] = datetime.datetime.strptime(a_kill['killmail_time'], '%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        # some older formats
                        try:
                            a_kill['kill_dt'] = datetime.datetime.strptime(a_kill['killmail_time'], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            a_kill['kill_dt'] = datetime.datetime.strptime(a_kill['killmail_time'], '%Y.%m.%d %H:%M:%S')
                    # now calculate how long ago it happened
                    delta = utcnow - a_kill['kill_dt']
                    a_kill['days_ago'] = delta.days
                    # convert to integers (zkillboard sends strings) and also initialize all keys used by templates
                    a_kill['victim']['characterID'] = 0
                    a_kill['victim']['characterName'] = ''
                    a_kill['victim']['corporationID'] = 0
                    a_kill['victim']['corporationName'] = ''
                    a_kill['victim']['allianceID'] = 0
                    a_kill['victim']['allianceName'] = ''
                    a_kill['victim']['shipTypeID'] = 0
                    a_kill['victim']['shipTypeName'] = ''
                    # fix character_id => characterID
                    if 'character_id' in a_kill['victim']:
                        a_kill['victim']['characterID'] = int(a_kill['victim']['character_id'])
                    # fix alliance_id => allianceID
                    if 'alliance_id' in a_kill['victim']:
                        a_kill['victim']['allianceID'] = int(a_kill['victim']['alliance_id'])
                    # fix corporation_id => corporationID
                    if 'corporation_id' in a_kill['victim']:
                        a_kill['victim']['corporationID'] = int(a_kill['victim']['corporation_id'])
                    # fix ship_type_id => shipTypeID
                    if 'ship_type_id' in a_kill['victim']:
                        a_kill['victim']['shipTypeID'] = int(a_kill['victim']['ship_type_id'])
                    # process attackers
                    for atk in a_kill['attackers']:
                        atk['characterID'] = 0
                        atk['characterName'] = ''
                        atk['corporationID'] = 0
                        atk['corporationName'] = ''
                        atk['allianceID'] = 0
                        atk['allianceName'] = ''
                        atk['shipTypeID'] = 0
                        atk['shipTypeName'] = ''
                        atk['finalBlow'] = atk['final_blow']
                        atk['factionID'] = 0
                        atk['factionName'] = ''
                        if 'character_id' in atk:
                            atk['characterID'] = atk['character_id']
                        if 'alliance_id' in atk:
                            atk['allianceID'] = atk['alliance_id']
                        if 'corporation_id' in atk:
                            atk['corporationID'] = atk['corporation_id']
                        if 'ship_type_id' in atk:
                            atk['shipTypeID'] = atk['ship_type_id']
                        if 'faction_id' in atk:
                            # this is an NPC kill
                            atk['factionID'] = atk['faction_id']
                            # NPC is not a character, zero out char name/id
                            atk['characterID'] = 0
                            atk['characterName'] = ''
                    finalBlow_attacker = dict()
                    for atk in a_kill['attackers']:
                        if atk['final_blow'] == True:
                            finalBlow_attacker = atk
                    a_kill['finalBlowAttacker'] = finalBlow_attacker
                    # fix solar system id
                    a_kill['solarSystemID'] = a_kill['solar_system_id']
                    # kill price in ISK
                    if 'zkb' in a_kill:
                        if 'totalValue' in a_kill['zkb']:
                            a_kill['zkb']['totalValueM'] = round(float(a_kill['zkb']['totalValue']) / 1000000.0)
            except KeyError as k_e:
                if self._debug:
                    print('It is possible that ZKB API has chabged (again).')
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
# kill[killID] -> 42298196
# kill[killTime] -> 2014-11-09 01:15:00
# kill[zkb] -> {u'source': u'API', u'totalValue': u'65945136.88', u'points': u'57'}
# kill[attackers] = list [ {u'corporationID': u'98045540', u'factionID': u'0',
#           u'securityStatus': u'4.55944451030535', u'weaponTypeID': u'27387',
#           u'characterName': u'xxxMASTERxxx', u'factionName': u'',
#           u'allianceName': u'Happy Cartel', u'finalBlow': u'1', u'allianceID':
#           u'99002411', u'shipTypeID': u'11993', u'corporationName': u'Stain Forever',
#           u'characterID': u'880181945', u'damageDone': u'6240'} ]
# kill[victim] -> {u'corporationID': u'1000107', u'factionID': u'0', u'damageTaken':
#           u'75855', u'characterName': u'Annet Svitch', u'factionName': u'',
#           u'allianceName': u'', u'allianceID': u'0', u'shipTypeID': u'16229',
#           u'corporationName': u'The Scope', u'victim': u'', u'characterID': u'95020841'}
# kill[items] -> list [ {u'typeID': u'30013', u'flag': u'5',
#           u'qtyDropped': u'8', u'singleton': u'0', u'qtyDestroyed': u'0'} ]
# kill[solarSystemID] -> 31000707
# kill[moonID] -> 0


if __name__ == '__main__':
    zkb_options_file = {
        'debug': True,
        'cache_time': 1200,
        'cache_type': 'file',
        'cache_dir': './_caches/zkb',
        'use_evekill': True
    }
    zkb_options_sqlite = {
        'debug': True,
        'cache_time': 1200,
        'cache_type': 'sqlite',
        'cache_file': './_caches/zkb/zkb_cache.db',
        'use_evekill': True
    }
    z = ZKB(zkb_options_file)
    # z = ZKB(zkb_options_sqlite)
    z.add_solarSystem('31000707')
    z.add_limit(1)
    zkb_kills = z.go()
    if len(zkb_kills) > 0:
        i = 0
        for a_kill in zkb_kills:
            if i == 0:
                pretty_print_kill(a_kill)
            i += 1

# end
#  for customs office:
# {'attackers': [
#   {
#       'allianceID': 0,
#       'allianceName': '',
#       'characterID': 94141200,
#       'characterName': 'Roman Askirason',
#       'corporationID': 98369889,
#       'corporationName': 'New Home Inc.',
#       'damageDone': 1407264,
#       'factionID': 0,
#       'factionName': '',
#       'finalBlow': 0, ...
#   },
#   {
#       'allianceID': 0,
#       'allianceName': '',
#       'characterID': 93485398,
#       'characterName': 'EVA Smitt',
#       'corporationID': 98142119,
#       'corporationName': 'Wormhole Piligrims',
#       'damageDone': 1205261,
#       'factionID': 0,
#       'factionName': '',
#       'finalBlow': 0, ...
#   }, ...
# ],
# 'items': [],
# 'killID': 44088489,
# 'killTime': '2015-01-23 20:47:00',
# 'moonID': 0,
# 'solarSystemID': 31001830,
# 'victim': {
#   'allianceID': 372230301,
#   'allianceName': 'Stellar Economy Experts',
#   'characterID': 0,
#   'characterName': '',
#   'corporationID': 677704765,
#   'corporationName': 'Global Economy Experts',
#   'damageTaken': 4480802,
#   'factionID': 0,
#   'factionName': '',
#   'shipTypeID': 2233
# },
# 'zkb': {
#   'hash': 'd9a74cd25b466b374680c3f82b14837f8db0f314',
#   'points': '237',
#   'source': 'CREST',
#   'totalValue': '114417658.89'}
# }

# how to convert date from kill to datetime structure:
# import datetime
# kill_dt = datetime.datetime.strptime(kill['killTime'], '%Y-%m-%d %H:%M:%S')