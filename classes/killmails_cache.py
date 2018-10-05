# -*- coding: utf-8 -*-
import sqlite3
import json
from classes.sitecfg import SiteConfig


class KillMailsCache:
    def __init__(self, siteconfig: SiteConfig):
        self._conn = sqlite3.connect(siteconfig.ZKB_CACHE_DIR + '/killmails.db', check_same_thread=False)
        self.check_tables()

    def check_tables(self):
        cur = self._conn.cursor()
        cur.execute('SELECT name FROM sqlite_master WHERE type=\'table\'')
        rows = cur.fetchall()
        tables = []
        for row in rows:
            tables.append(str(row[0]))

        if 'killmails' not in tables:
            q = 'CREATE TABLE killmails (kill_id TEXT, kill_hash TEXT, json TEXT, PRIMARY KEY(kill_id, kill_hash))'
            cur.execute(q)
            self._conn.commit()
        cur.close()

    def get_killmail(self, kill_id: str, kill_hash: str) -> dict:
        ret = {}
        cur = self._conn.cursor()
        cur.execute('SELECT json FROM killmails WHERE kill_id=? AND kill_hash=?', (kill_id, kill_hash))
        rows = cur.fetchall()
        if len(rows) > 0:
            json_str = rows[0][0]
            if json_str != '':
                try:
                    ret = json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        cur.close()
        return ret

    def save_killmail(self, kill_id: str, kill_hash: str, killmail: object):
        json_text = json.dumps(killmail)
        cur = self._conn.cursor()
        cur.execute('INSERT OR REPLACE INTO killmails (kill_id, kill_hash, json) VALUES (?,?,?)',
                    (kill_id, kill_hash, json_text))
        self._conn.commit()
        cur.close()
