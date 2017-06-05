# -*- coding: utf-8 -*-

import configparser


class SiteConfig:
    def __init__(self, cfg_filename='whdbx_config.ini'):
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

        self.SSO_CLIENT_ID = ''
        self.SSO_SECRET_KEY = ''
        self.SSO_SCOPES = ''
        self.SSO_CALLBACK_URL = ''

        self.load(cfg_filename)

    def load(self, cfg_filename='whdbx_config.ini'):
        cfg = configparser.ConfigParser(allow_no_value=True)
        read_files = cfg.read(cfg_filename)
        if cfg_filename not in read_files:
            return

        self.DEBUG = cfg['general'].getboolean('DEBUG')
        self.EMULATE = cfg['general'].getboolean('EMULATE')

        # template vars
        if cfg.has_section('dirs'):
            self.TEMPLATE_DIR = cfg['dirs']['template_dir']
            self.TEMPLATE_CACHE_DIR = cfg['dirs']['template_cache_dir']
        # sqlite
        if cfg.has_section('sqlite'):
            self.EVEDB = cfg['sqlite']['evedb']
            self.ROUTES_CACHE_DIR = cfg['sqlite']['routes_cache_dir']
        # zkb
        if cfg.has_section('zkillboard'):
            self.ZKB_CACHE_TYPE = cfg['zkillboard']['cache_type']
            self.ZKB_CACHE_TIME = int(cfg['zkillboard']['cache_time'])
            self.ZKB_CACHE_DIR = cfg['zkillboard']['cache_dir']
            self.ZKB_CACHE_SQLITE = cfg['zkillboard']['cache_sqlite']
            self.ZKB_USE_EVEKILL = cfg['zkillboard'].getboolean('use_evekill')
        # eve-central
        if cfg.has_section('evecentral'):
            self.EVECENTRAL_CACHE_DIR = cfg['evecentral']['evecentral_cache_dir']
            self.EVECENTRAL_CACHE_HOURS = int(cfg['evecentral']['evecentral_cache_hours'])
        # eve-sso
        if cfg.has_section('sso'):
            self.SSO_CLIENT_ID = str(cfg['sso']['client_id'])
            self.SSO_SECRET_KEY = str(cfg['sso']['secret_key'])
            self.SSO_SCOPES = str(cfg['sso']['scopes'])
            self.SSO_CALLBACK_URL = str(cfg['sso']['callback_url'])
