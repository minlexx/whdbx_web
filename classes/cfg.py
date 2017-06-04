# -*- coding: utf-8 -*-

import configparser


class SiteCfg:
    def __init__(self, cfg_filename='whdbx_config.ini'):
        self._cfg = None

        self.DEBUG = False
        self.EMULATE = False

        self.TEMPLATE_DIR = '.'
        self.TEMPLATE_CACHE_DIR = '.'

        self.EVEDB = ''
        self.ROUTES_CACHE_DIR = '.'

        self.ZKB_CACHE_TYPE = 'file'
        self.ZKB_CACHE_TIME = 1200
        self.ZKB_CACHE_DIR = '.'
        self.ZKB_CACHE_SQLITE = ''
        self.ZKB_USE_EVEKILL = False

        self.EVECENTRAL_CACHE_DIR = ''
        self.EVECENTRAL_CACHE_HOURS = 24

        self.load(cfg_filename)

    def load(self, cfg_filename='whdbx_config.ini'):
        if self._cfg:
            del self._cfg
        self._cfg = configparser.ConfigParser(allow_no_value=True)
        read_files = self._cfg.read(cfg_filename)
        if cfg_filename not in read_files:
            return
        if cfg_filename in read_files:
            self.DEBUG = self._cfg['general'].getboolean('DEBUG')
            self.EMULATE = self._cfg['general'].getboolean('EMULATE')

            # template vars
            if self._cfg.has_section('dirs'):
                self.TEMPLATE_DIR = self._cfg['dirs']['template_dir']
                self.TEMPLATE_CACHE_DIR = self._cfg['dirs']['template_cache_dir']
            # sqlite
            if self._cfg.has_section('sqlite'):
                self.EVEDB = self._cfg['sqlite']['evedb']
                self.ROUTES_CACHE_DIR = self._cfg['sqlite']['routes_cache_dir']
            # zkb
            if self._cfg.has_section('zkillboard'):
                self.ZKB_CACHE_TYPE = self._cfg['zkillboard']['cache_type']
                self.ZKB_CACHE_TIME = int(self._cfg['zkillboard']['cache_time'])
                self.ZKB_CACHE_DIR = self._cfg['zkillboard']['cache_dir']
                self.ZKB_CACHE_SQLITE = self._cfg['zkillboard']['cache_sqlite']
                self.ZKB_USE_EVEKILL = self._cfg['zkillboard'].getboolean('use_evekill')
            # eve-central
            if self._cfg.has_section('evecentral'):
                self.EVECENTRAL_CACHE_DIR = self._cfg['evecentral']['evecentral_cache_dir']
                self.EVECENTRAL_CACHE_HOURS = int(self._cfg['evecentral']['evecentral_cache_hours'])
        del self._cfg
        self._cfg = None
