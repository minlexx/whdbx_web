# -*- coding: utf-8 -*-
import json
import sqlite3
import threading

from . import sitecfg


class EveNamesDb:
    def __init__(self, siteconfig: sitecfg.SiteConfig):
        self._conn = sqlite3.connect(siteconfig.NAMES_DB, check_same_thread=False)
        self._write_lock = threading.Lock()
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

    def resolve_characters_names(self, ids_list) -> list:
        pass

    def resolve_corporations_names(self, ids_list) -> list:
        pass

    def resolve_alliances_names(self, ids_list) -> list:
        pass
