# -*- coding: utf-8 -*-

import configparser
import urllib.parse


class SiteConfig:
    def __init__(self):
        self.DEBUG = False
        self.EMULATE = False

        self.TEMPLATE_DIR = '.'
        self.TEMPLATE_CACHE_DIR = '.'

        self.SESSION_TYPE = 'memory'
        self.SESSION_TIME_MINUTES = 60
        self.SESSION_FILES_DIR = '.'
        self.SESSION_REDIS_HOST = 'localhost'
        self.SESSION_REDIS_PORT = 6379
        self.SESSION_REDIS_DB = 0

        self.EVEDB = ''
        self.ROUTES_CACHE_DIR = '.'
        self.NAMES_DB = ''

        self.ZKB_CACHE_TYPE = 'file'
        self.ZKB_CACHE_TIME = 1200
        self.ZKB_CACHE_DIR = '.'
        self.ZKB_CACHE_SQLITE = ''
        self.ZKB_USE_EVEKILL = False
        self.ZKB_KILLS_ON_PAGE = 30

        self.PRICE_RESOLVER = 'esi'
        self.EVECENTRAL_CACHE_DIR = ''
        self.EVECENTRAL_CACHE_HOURS = 24

        self.ESI_BASE_URL = ''
        self.SSO_CLIENT_ID = ''
        self.SSO_SECRET_KEY = ''
        self.SSO_SCOPES = ''
        self.SSO_CALLBACK_URL = ''
        self.SSO_USER_AGENT = ''

        self.load('whdbx_config.ini')
        self.load('whdbx_config_local.ini')

    def load(self, cfg_filename: str):
        cfg = configparser.ConfigParser(allow_no_value=True)
        read_files = cfg.read(cfg_filename)
        if cfg_filename not in read_files:
            return

        if cfg.has_section('general'):
            if 'DEBUG' in cfg['general']:
                self.DEBUG = cfg['general'].getboolean('DEBUG')
            if 'EMULATE' in cfg['general']:
                self.EMULATE = cfg['general'].getboolean('EMULATE')

            # template vars
            if 'template_dir' in cfg['general']:
                self.TEMPLATE_DIR = cfg['general']['template_dir']
            if 'template_cache_dir' in cfg['general']:
                self.TEMPLATE_CACHE_DIR = cfg['general']['template_cache_dir']

            # session vars
            if 'session_storage_type' in cfg['general']:
                self.SESSION_TYPE = str(cfg['general']['session_storage_type'])
            if 'session_time_minutes' in cfg['general']:
                self.SESSION_TIME_MINUTES = int(cfg['general']['session_time_minutes'])
            if 'session_files_dir' in cfg['general']:
                self.SESSION_FILES_DIR = str(cfg['general']['session_files_dir'])
            if 'session_redis_host' in cfg['general']:
                self.SESSION_REDIS_HOST = str(cfg['general']['session_redis_host'])
            if 'session_redis_port' in cfg['general']:
                self.SESSION_REDIS_PORT = str(cfg['general']['session_redis_port'])
            if 'session_redis_db' in cfg['general']:
                self.SESSION_REDIS_DB = str(cfg['general']['session_redis_db'])

        # sqlite
        if cfg.has_section('sqlite'):
            if 'evedb' in cfg['sqlite']:
                self.EVEDB = cfg['sqlite']['evedb']
            if 'routes_cache_dir' in cfg['sqlite']:
                self.ROUTES_CACHE_DIR = cfg['sqlite']['routes_cache_dir']
            if 'names_db' in cfg['sqlite']:
                self.NAMES_DB = cfg['sqlite']['names_db']

        # zkb
        if cfg.has_section('zkillboard'):
            if 'cache_type' in cfg['zkillboard']:
                self.ZKB_CACHE_TYPE = cfg['zkillboard']['cache_type']
            if 'cache_time' in cfg['zkillboard']:
                self.ZKB_CACHE_TIME = int(cfg['zkillboard']['cache_time'])
            if 'cache_dir' in cfg['zkillboard']:
                self.ZKB_CACHE_DIR = cfg['zkillboard']['cache_dir']
            if 'cache_sqlite' in cfg['zkillboard']:
                self.ZKB_CACHE_SQLITE = cfg['zkillboard']['cache_sqlite']
            if 'use_evekill' in cfg['zkillboard']:
                self.ZKB_USE_EVEKILL = cfg['zkillboard'].getboolean('use_evekill')
            if 'kills_on_page' in cfg['zkillboard']:
                self.ZKB_KILLS_ON_PAGE = int(cfg['zkillboard']['kills_on_page'])

        # eve-central
        if cfg.has_section('evecentral'):
            if 'price_resolver' in cfg['evecentral']:
                self.PRICE_RESOLVER = cfg['evecentral']['price_resolver']
            if 'evecentral_cache_dir' in cfg['evecentral']:
                self.EVECENTRAL_CACHE_DIR = cfg['evecentral']['evecentral_cache_dir']
            if 'evecentral_cache_hours' in cfg['evecentral']:
                self.EVECENTRAL_CACHE_HOURS = int(cfg['evecentral']['evecentral_cache_hours'])

        # eve-sso
        if cfg.has_section('sso'):
            if 'esi_base_url' in cfg['sso']:
                self.ESI_BASE_URL = str(cfg['sso']['esi_base_url'])
            if 'client_id' in cfg['sso']:
                self.SSO_CLIENT_ID = str(cfg['sso']['client_id'])
            if 'secret_key' in cfg['sso']:
                self.SSO_SECRET_KEY = str(cfg['sso']['secret_key'])
            if 'scopes' in cfg['sso']:
                self.SSO_SCOPES = str(cfg['sso']['scopes'])
            if 'callback_url' in cfg['sso']:
                self.SSO_CALLBACK_URL = str(cfg['sso']['callback_url'])
            if 'user_agent' in cfg['sso']:
                self.SSO_USER_AGENT = str(cfg['sso']['user_agent'])

    def sso_login_url(self, optional_state: str = ''):
        url = 'https://login.eveonline.com/oauth/authorize'
        url += '?response_type=code'
        url += '&amp;redirect_uri='
        url += urllib.parse.quote_plus(self.SSO_CALLBACK_URL)
        url += '&amp;client_id='
        url += urllib.parse.quote_plus(self.SSO_CLIENT_ID)
        url += '&amp;scope='
        url += urllib.parse.quote_plus(self.SSO_SCOPES)
        if optional_state != '':
            url += '&amp;state='
            url += optional_state
        return url