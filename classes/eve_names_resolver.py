# -*- coding: utf-8 -*-
import sqlite3
import threading
import sys

from . import sitecfg
from . import esi_calls


class EsiNamesResolver:
    def __init__(self, cfg: sitecfg.SiteConfig):
        self.cfg = cfg
        self.error_str = ''
        self.ids_limit = 10
        self.universe_ids_limit = 1000

    def resolve_universe_names(self, ids_list: list) -> list:
        ret = []
        self.error_str = ''  # clear error indicator
        try:
            if len(ids_list) > self.universe_ids_limit:
                # request part by part
                while len(ids_list) > 0:
                    ids_list_part = ids_list[0:self.universe_ids_limit]  # get first LIMIT elemnts
                    ids_list = ids_list[self.universe_ids_limit:]        # cut first LIMIT elements
                    subret = esi_calls.universe_names(self.cfg, ids_list_part)
                    for item in subret:
                        ret.append(item)
            else:
                ret = esi_calls.universe_names(self.cfg, ids_list)
        except esi_calls.ESIException as ex:
            self.error_str = ex.error_string()
        return ret


class EveNamesDb:
    def __init__(self, siteconfig: sitecfg.SiteConfig):
        self._conn = sqlite3.connect(siteconfig.NAMES_DB, check_same_thread=False)
        self._write_lock = threading.Lock()
        self._resolver = EsiNamesResolver(siteconfig)
        self.check_tables()

    def check_tables(self):
        """
        Automatically create needed tables if not exist
        :return: None
        """
        self._write_lock.acquire()
        existing_tables = []
        cur = self._conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for row in cur:
            existing_tables.append(row[0])
        cur.close()
        if 'charnames' not in existing_tables:
            cur = self._conn.cursor()
            cur.execute('CREATE TABLE charnames (id INTEGER PRIMARY KEY NOT NULL, name TEXT)')
            self._conn.commit()
            cur.close()
        if 'corpnames' not in existing_tables:
            cur = self._conn.cursor()
            cur.execute('CREATE TABLE corpnames (id INTEGER PRIMARY KEY NOT NULL, name TEXT)')
            self._conn.commit()
            cur.close()
        if 'allynames' not in existing_tables:
            cur = self._conn.cursor()
            cur.execute('CREATE TABLE allynames (id INTEGER PRIMARY KEY NOT NULL, name TEXT)')
            self._conn.commit()
            cur.close()
        self._write_lock.release()

    def get_char_name(self, iid: int) -> str:
        if iid <= 0: return ''
        cur = self._conn.cursor()
        cur.execute('SELECT name FROM charnames WHERE id = ?', (iid,))
        row = cur.fetchone()
        cur.close()
        if row is not None:
            return row[0]
        return ''

    def get_corp_name(self, iid: int) -> str:
        if iid <= 0: return ''
        cur = self._conn.cursor()
        cur.execute('SELECT name FROM corpnames WHERE id = ?', (iid,))
        row = cur.fetchone()
        cur.close()
        if row is not None:
            return row[0]
        return ''

    def get_ally_name(self, iid: int) -> str:
        if iid <= 0: return ''
        cur = self._conn.cursor()
        cur.execute('SELECT name FROM allynames WHERE id = ?', (iid,))
        row = cur.fetchone()
        cur.close()
        if row is not None:
            return row[0]
        return ''

    def set_char_name(self, iid: int, name: str) -> None:
        if iid <= 0: return
        self._write_lock.acquire()
        cur = self._conn.cursor()
        cur.execute('INSERT OR REPLACE INTO charnames (id, name) VALUES (?, ?)', (iid, name))
        self._conn.commit()
        cur.close()
        self._write_lock.release()

    def set_corp_name(self, iid: int, name: str) -> None:
        if iid <= 0: return
        self._write_lock.acquire()
        cur = self._conn.cursor()
        cur.execute('INSERT OR REPLACE INTO corpnames (id, name) VALUES (?, ?)', (iid, name))
        self._conn.commit()
        cur.close()
        self._write_lock.release()

    def set_ally_name(self, iid: int, name: str) -> None:
        if iid <= 0: return
        self._write_lock.acquire()
        cur = self._conn.cursor()
        cur.execute('INSERT OR REPLACE INTO allynames (id, name) VALUES (?, ?)', (iid, name))
        self._conn.commit()
        cur.close()
        self._write_lock.release()

    def fill_names_in_zkb_kills(self, kills: list) -> list:
        # 1. collect unknown IDs
        unknown_charids = []
        unknown_corpids = []
        unknown_allyids = []
        for kill in kills:
            if 'character_id' in kill['victim']:
                char_id = int(kill['victim']['character_id'])
                char_name = self.get_char_name(char_id)
                if (char_name == '') and (char_id > 0):  # add to unknowns
                    unknown_charids.append(char_id)
            if 'corporation_id' in kill['victim']:
                corp_id = int(kill['victim']['corporation_id'])
                corp_name = self.get_corp_name(corp_id)
                if (corp_name == '') and (corp_id >= 0):
                    unknown_corpids.append(corp_id)
            if 'alliance_id' in kill['victim']:
                ally_id = int(kill['victim']['alliance_id'])
                ally_name = self.get_ally_name(ally_id)
                if (ally_name == '') and (ally_id >= 0):
                    unknown_allyids.append(ally_id)
            for atk in kill['attackers']:
                if 'character_id' in atk:
                    char_id = int(atk['character_id'])
                    char_name = self.get_char_name(char_id)
                    if (char_name == '') and (char_id >= 0):
                        unknown_charids.append(char_id)
                if 'corporation_id' in atk:
                    corp_id = int(atk['corporation_id'])
                    corp_name = self.get_corp_name(corp_id)
                    if (corp_name == '') and (corp_id >= 0):
                        unknown_corpids.append(corp_id)
                if 'alliance_id' in atk:
                    ally_id = int(atk['alliance_id'])
                    ally_name = self.get_ally_name(ally_id)
                    if (ally_name == '') and (ally_id >= 0):
                        unknown_allyids.append(ally_id)

        # 2. make a skingle universe_names request for all IDs types
        #  (characters, corporations, alliances) - all at once
        all_unknown_ids = unknown_charids + unknown_corpids + unknown_allyids
        names = self._resolver.resolve_universe_names(all_unknown_ids)
        if self._resolver.error_str != '':
            print('names resolving error: {}'.format(self._resolver.error_str), file=sys.stderr)
            print('names resolving error:  ids were: {}'.format(all_unknown_ids), file=sys.stderr)
        for obj in names:
            # [{'category': 'character', 'name': 'Xxx', 'id': 2114246032}, {...}, ...]
            cat = obj['category']
            # category may be one of:
            #  [ alliance, character, constellation, corporation, inventory_type, region, solar_system, station ]
            if cat == 'character':
                self.set_char_name(obj['id'], obj['name'])
            elif cat == 'corporation':
                self.set_corp_name(obj['id'], obj['name'])
            elif cat == 'alliance':
                self.set_ally_name(obj['id'], obj['name'])

        # 3. fill in gathered information
        for kill in kills:
            victim = kill['victim']
            if 'character_id' in victim:
                char_id = int(victim['character_id'])
                if char_id > 0:
                    char_name = self.get_char_name(char_id)
                    if char_name != '':
                        victim['characterName'] = char_name
            if 'corporation_id' in victim:
                corp_id = int(victim['corporation_id'])
                if corp_id > 0:
                    corp_name = self.get_corp_name(corp_id)
                    if corp_name != '':
                        victim['corporationName'] = corp_name
            if 'alliance_id' in victim:
                ally_id = int(victim['alliance_id'])
                if ally_id > 0:
                    ally_name = self.get_ally_name(ally_id)
                    if ally_name != '':
                        victim['allianceName'] = ally_name
            for atk in kill['attackers']:
                if 'character_id' in atk:
                    char_id = int(atk['character_id'])
                    if char_id > 0:
                        char_name = self.get_char_name(char_id)
                        if char_name != '':
                            atk['characterName'] = char_name
                if 'corporation_id' in atk:
                    corp_id = int(atk['corporation_id'])
                    if corp_id > 0:
                        corp_name = self.get_corp_name(corp_id)
                        if corp_name != '':
                            atk['corporationName'] = corp_name
                if 'alliance_id' in atk:
                    ally_id = int(atk['alliance_id'])
                    if ally_id > 0:
                        ally_name = self.get_ally_name(ally_id)
                        if ally_name != '':
                            atk['allianceName'] = ally_name

        return kills
