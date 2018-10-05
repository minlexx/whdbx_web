#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import logging
import os
import os.path
import pathlib
import re
import uuid

import cherrypy
from cherrypy._cpdispatch import Dispatcher
import cherrypy.lib.sessions

import requests
import requests.exceptions

from classes.sitecfg import SiteConfig
from classes.template_engine import TemplateEngine
from classes.database import SiteDb, WHClass, get_ss_security_color
from classes.eve_names_resolver import EveNamesDb
from classes.sleeper import WHSleeper
from classes.signature import WHSignature
from classes.zkillboard import ZKB
from classes.whsystem import WHSystem
from classes.utils import dump_object, is_whsystem_name
from classes import esi_calls
from classes import error_pages
from classes import tr_support


class WhdbxApp:

    class CustomDispatcher(Dispatcher):
        sleepers_id_match = re.compile(r'/sleepers/([0-9]+)/')
        signatures_id_match = re.compile(r'/signatures/([0-9]+)/')

        def __call__(self, path_info: str):
            path_info = path_info.lower()
            # check that requested path is in form 'J123456' ('/j170122')
            # redirects /J123456 to /ss/?jsystem=J123456
            if len(path_info) > 1:
                # fix for development environment
                if path_info == '/eve_sso_callback.py':
                    return Dispatcher.__call__(self, '/eve_sso_callback/')
                #
                jsystem_name = path_info[1:]  # remove leading '/'
                if is_whsystem_name(jsystem_name):
                    cherrypy.request.params['jsystem'] = jsystem_name
                    return Dispatcher.__call__(self, '/ss')
                m = self.sleepers_id_match.match(path_info)
                if m is not None:
                    cherrypy.request.params['id'] = m.group(1)
                    return Dispatcher.__call__(self, '/sleepers/')
                m = self.signatures_id_match.match(path_info)
                if m is not None:
                    cherrypy.request.params['id'] = m.group(1)
                    return Dispatcher.__call__(self, '/signatures/')
            return Dispatcher.__call__(self, path_info)

    def __init__(self):
        self.rootdir = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).as_posix()
        self.cfg = SiteConfig()
        self.tmpl = TemplateEngine(self.cfg)
        self.db = SiteDb(self.cfg)
        self.names_db = EveNamesDb(self.cfg)

        # options for zkillboard helper
        self.zkb_options = {
            'debug': False,
            'cache_time': self.cfg.ZKB_CACHE_TIME,
            'cache_type': self.cfg.ZKB_CACHE_TYPE,
            'cache_dir': self.cfg.ZKB_CACHE_DIR,
            'use_evekill': self.cfg.ZKB_USE_EVEKILL,
            'kills_on_page': self.cfg.ZKB_KILLS_ON_PAGE
        }

        # session vars declaration
        self.needed_session_vars = [
            'sso_token', 'sso_refresh_token',
            'sso_expire_dt', 'sso_expire_dt_utc',
            'sso_char_id', 'sso_char_name',
            'sso_corp_id', 'sso_corp_name', 'sso_ally_id',
            'sso_ship_id', 'sso_ship_name', 'sso_ship_title',
            'sso_solarsystem_id', 'sso_solarsystem_name',
            'configured_locale'
        ]

        # logging setup
        self.tag = 'WHDBX'
        cherrypy.log.screen = self.cfg.DEBUG  # enable cherrypy logging to console only in DEBUG

        # translations setup
        self.translations_dir = self.rootdir + '/locales'
        self.tr = tr_support.MultiLangTranslator(self.translations_dir, 'whdbx')
        self.tr.init_translations()

        # options for cherrypy application
        session_storage_class = cherrypy.lib.sessions.RamSession
        session_storage_path = os.path.abspath(self.cfg.SESSION_FILES_DIR)
        if self.cfg.SESSION_TYPE == 'file':
            session_storage_class = cherrypy.lib.sessions.FileSession
            # verify that sessions directory actually exists
            if not os.path.isdir(session_storage_path):
                self.debuglog('Creating session file storage: ', session_storage_path)
                os.makedirs(session_storage_path)
        elif self.cfg.SESSION_TYPE == 'memcache':
            session_storage_class = cherrypy.lib.sessions.MemcachedSession
        elif self.cfg.SESSION_TYPE == 'redis':
            from classes.redis_session import WhdbxRedisSession
            session_storage_class = WhdbxRedisSession
        else:
            cherrypy.log('Unknown value for session_storage_type: "{}"; using memory session.'.format(
                self.cfg.SESSION_TYPE), self.tag, logging.WARNING)
        self.cherrypy_config = {
            '/': {
                'request.dispatch': WhdbxApp.CustomDispatcher(),
                'tools.sessions.on': True,
                'tools.sessions.storage_class': session_storage_class,
                'tools.sessions.storage_path': session_storage_path,
                'tools.sessions.timeout': self.cfg.SESSION_TIME_MINUTES,
                'tools.sessions.redis_host': self.cfg.SESSION_REDIS_HOST,
                'tools.sessions.redis_port': self.cfg.SESSION_REDIS_PORT,
                'tools.sessions.redis_db': self.cfg.SESSION_REDIS_DB,
                'tools.staticdir.root': self.rootdir,
                'error_page.404': error_pages.page_404,
                'error_page.500': error_pages.page_500
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': './static'
            }
        }

        self.debuglog('started, rootdir=[{}]'.format(self.rootdir))
        self.debuglog('loaded locales: {}'.format(self.tr.supported_locales))

    def get_cherrypy_app_config(self) -> dict:
        return self.cherrypy_config

    def debugprint(self, msg: str = '',
                   show_config: bool = True,
                   show_env: bool = True) -> str:
        res = ''
        cherrypy.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        if show_config:
            res += 'use evekill: ' + str(self.cfg.ZKB_USE_EVEKILL) + '\n'
        if show_env:
            res += str(os.environ) + '\n\n'
        res += msg
        return res

    def debuglog(self, *args):
        if not self.cfg.DEBUG: return
        s = ''
        for a in args: s += str(a)
        cherrypy.log(s, self.tag)

    # call this if any input error
    def display_failure(self, comment: str = '') -> str:
        if not self.tmpl.is_set('title'):
            self.tmpl.assign('title', 'ERROR - WHDBX')
        self.tmpl.assign('MODE', 'failure')  # current page identifier
        # assign EVE-SSO data defaults
        self.tmpl.assign('HAVE_SSO_LOGIN', False)
        self.tmpl.assign('SSO_TOKEN_EXPIRE_DT', '')
        self.tmpl.assign('SSO_LOGIN_URL', self.cfg.sso_login_url(cherrypy.session['sso_state']))
        self.tmpl.assign('SSO_CHAR_ID', '')
        self.tmpl.assign('SSO_CHAR_NAME', '')
        self.tmpl.assign('SSO_CORP_ID', '')
        self.tmpl.assign('SSO_CORP_NAME', '')
        self.tmpl.assign('SSO_SHIP_ID', '')
        self.tmpl.assign('SSO_SHIP_NAME', '')
        self.tmpl.assign('SSO_SHIP_TITLE', '')
        self.tmpl.assign('SSO_SOLARSYSTEM_ID', '')
        self.tmpl.assign('SSO_SOLARSYSTEM_NAME', '')
        self.tmpl.assign('SSO_ONLINE', '')
        self.setup_locale()
        self.tmpl.assign('error_comment', comment)
        return self.tmpl.render('failure.html')

    def init_session(self):
        # create all needed default values in session
        if 'sso_state' not in cherrypy.session:
            new_state = uuid.uuid4().hex
            cherrypy.session['sso_state'] = new_state
            self.debuglog('Generated new sso_state = {}'.format(new_state))
        # auto-create missing session vars as empty strings
        for var_name in self.needed_session_vars:
            if var_name not in cherrypy.session:
                cherrypy.session[var_name] = ''

    def sso_session_cleanup(self):
        for var_name in self.needed_session_vars:
            cherrypy.session[var_name] = ''
        del cherrypy.session['sso_state']
        self.debuglog('session cleaned')

    @staticmethod
    def is_ip_admin() -> bool:
        if 'remote-addr' not in cherrypy.request.headers:
            return False
        # We may be behind nginx reverse-proxy with setup privding X-Real-Ip:
        if 'x-real-ip' in cherrypy.request.headers:
            ip = cherrypy.request.headers['x-real-ip']
        else:
            ip = cherrypy.request.headers['remote-addr']
        if ip.startswith('127.') or ip.startswith('192.168.') or ip.startswith('172.16.') or ip.startswith('10.'):
            return True
        return False

    def parse_client_accept_language(self) -> str:
        """
        Parse HTTP header Accept-Language, which can be in form:
        - Accept-Language: de
        - Accept-Language: de-CH
        - Accept-Language: en-US,en;q=0.5
        :return: first 2 letters of header, or empty string if no header found.
        """
        ret = ''
        if 'accept-language' in cherrypy.request.headers:
            accept_language = cherrypy.request.headers['accept-language']
            ret = accept_language[0:2]
            self.debuglog('detected language: {}'.format(ret))
        else:
            self.debuglog('cannot detect language!')
        return ret

    def get_selected_locale_code(self) -> str:
        """
        Determine what locale to use to translate user-visible sstrings
        for *current* client request. Try to look for preconfigured value in
        session, or try to parse Accept-Language HTTP header. In case of
        no locale can be determined, or locale unsupported, return 'en'
        :return: string, 'en', 'ru', etc. Always returns valid value
        """
        selected_locale = ''
        # first, check that user has configured language. Then don't autodetect
        if 'configured_locale' in cherrypy.session:
            if cherrypy.session['configured_locale'] != '':
                configured_locale = cherrypy.session['configured_locale']
                if configured_locale in self.tr.supported_locales:
                    selected_locale = configured_locale
        # no user-configured locale, try to autodetect
        if selected_locale == '':
            accept_language = self.parse_client_accept_language()
            if accept_language != '':
                selected_locale = accept_language
        # fallback to english
        if selected_locale == '':
            selected_locale = 'en'
        return selected_locale

    def gettext(self, msg) -> str:
        """
        Translate msg using current request's locale
        :param msg:
        :return: translated msg, if locale is supported; otherwise return original msg
        """
        lc = self.get_selected_locale_code()
        tr = self.tr.get_translator(lc)
        if tr is None:
            return msg
        return tr.gettext(msg)

    @cherrypy.expose()
    def dump_session(self, **params):
        if not self.is_ip_admin():
            return self.debugprint('Access denied', show_config=False, show_env=False)
        text = 'Session dump:\n'
        keys = cherrypy.session.keys()
        for key in keys:
            value = str(cherrypy.session[key])
            text += "  cherrypy.session['{}'] = '{}'\n".format(str(key), value)
        #
        return self.debugprint(text, show_config=False, show_env=False)

    @cherrypy.expose()
    def dump_headers(self, **params):
        msg = ''
        for h in cherrypy.request.headers:
            msg += str(h) + ': ' + str(cherrypy.request.headers[h]) + '\n'
        return self.debugprint(msg, show_config=False, show_env=False)

    @cherrypy.expose()
    def test_failure(self, **params):
        return self.display_failure('Test failure')

    @cherrypy.expose()
    def adm_reload_config(self, **params):
        if not self.is_ip_admin():
            return self.debugprint('Access denied', show_config=False, show_env=False)
        self.cfg.load('whdbx_config.ini')
        self.cfg.load('whdbx_config_local.ini')
        # enable cherrypy logging to console only in DEBUG
        cherrypy.log.screen = self.cfg.DEBUG
        # reload also ZKB options
        self.zkb_options = {
            'debug': False,
            'cache_time': self.cfg.ZKB_CACHE_TIME,
            'cache_type': self.cfg.ZKB_CACHE_TYPE,
            'cache_dir': self.cfg.ZKB_CACHE_DIR,
            'use_evekill': self.cfg.ZKB_USE_EVEKILL,
            'kills_on_page': self.cfg.ZKB_KILLS_ON_PAGE
        }
        # output
        msg = '\n'
        msg += 'DEBUG: {}\n'.format(self.cfg.DEBUG)
        msg += 'EMULATE: {}\n'.format(self.cfg.EMULATE)
        msg += 'TEMPLATE_DIR: {}\n'.format(self.cfg.TEMPLATE_DIR)
        msg += 'TEMPLATE_CACHE_DIR: {}\n'.format(self.cfg.TEMPLATE_CACHE_DIR)
        msg += 'EVEDB: {}\n'.format(self.cfg.EVEDB)
        msg += 'ROUTES_CACHE_DIR: {}\n'.format(self.cfg.ROUTES_CACHE_DIR)
        msg += 'ZKB_CACHE_TYPE: {}\n'.format(self.cfg.ZKB_CACHE_TYPE)
        msg += 'ZKB_CACHE_TIME: {}\n'.format(self.cfg.ZKB_CACHE_TIME)
        msg += 'ZKB_CACHE_DIR: {}\n'.format(self.cfg.ZKB_CACHE_DIR)
        msg += 'ZKB_CACHE_SQLITE: {}\n'.format(self.cfg.ZKB_CACHE_SQLITE)
        msg += 'ZKB_USE_EVEKILL: {}\n'.format(self.cfg.ZKB_USE_EVEKILL)
        msg += 'EVECENTRAL_CACHE_DIR: {}\n'.format(self.cfg.EVECENTRAL_CACHE_DIR)
        msg += 'EVECENTRAL_CACHE_HOURS: {}\n'.format(self.cfg.EVECENTRAL_CACHE_HOURS)
        msg += 'ESI_BASE_URL: {}\n'.format(self.cfg.ESI_BASE_URL)
        msg += 'SSO_CLIENT_ID: {}\n'.format(self.cfg.SSO_CLIENT_ID)
        msg += 'SSO_SECRET_KEY: {}\n'.format(self.cfg.SSO_SECRET_KEY)
        msg += 'SSO_SCOPES: {}\n'.format(self.cfg.SSO_SCOPES)
        msg += 'SSO_CALLBACK_URL: {}\n'.format(self.cfg.SSO_CALLBACK_URL)
        msg += 'SSO_USER_AGENT: {}\n'.format(self.cfg.SSO_USER_AGENT)
        msg += '\nDatabase was not reconnected; Template engine was not reloaded here.\n'
        msg += 'You need to fully restart server to do this.\n'
        return self.debugprint(msg, show_config=False, show_env=False)

    def setup_template_vars(self, page: str = ''):
        self.tmpl.unassign_all()
        self.tmpl.assign('title', 'WHDBX')  # default title
        self.tmpl.assign('error_comment', '')  # should be always defined!
        self.tmpl.assign('MODE', page)  # current page identifier
        self.tmpl.assign('sitecfg', self.cfg)
        # assign EVE-SSO data defaults
        self.tmpl.assign('HAVE_SSO_LOGIN', False)
        self.tmpl.assign('SSO_TOKEN_EXPIRE_DT', '')
        self.tmpl.assign('SSO_LOGIN_URL', self.cfg.sso_login_url(cherrypy.session['sso_state']))
        self.tmpl.assign('SSO_CHAR_ID', '')
        self.tmpl.assign('SSO_CHAR_NAME', '')
        self.tmpl.assign('SSO_CORP_ID', '')
        self.tmpl.assign('SSO_CORP_NAME', '')
        self.tmpl.assign('SSO_SHIP_ID', '')
        self.tmpl.assign('SSO_SHIP_NAME', '')
        self.tmpl.assign('SSO_SHIP_TITLE', '')
        self.tmpl.assign('SSO_SOLARSYSTEM_ID', '')
        self.tmpl.assign('SSO_SOLARSYSTEM_NAME', '')
        self.tmpl.assign('SSO_ONLINE', '')
        if cherrypy.session['sso_token'] != '':
            self.tmpl.assign('HAVE_SSO_LOGIN', True)
            self.tmpl.assign('SSO_TOKEN_EXPIRE_DT',
                cherrypy.session['sso_expire_dt_utc'].strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.tmpl.assign('SSO_CHAR_ID', cherrypy.session['sso_char_id'])
            self.tmpl.assign('SSO_CHAR_NAME', cherrypy.session['sso_char_name'])
            self.tmpl.assign('SSO_CORP_ID', cherrypy.session['sso_corp_id'])
            self.tmpl.assign('SSO_CORP_NAME', cherrypy.session['sso_corp_name'])
            self.tmpl.assign('SSO_SHIP_ID', cherrypy.session['sso_ship_id'])
            self.tmpl.assign('SSO_SHIP_NAME', cherrypy.session['sso_ship_name'])
            self.tmpl.assign('SSO_SHIP_TITLE', cherrypy.session['sso_ship_title'])
            self.tmpl.assign('SSO_SOLARSYSTEM_ID', cherrypy.session['sso_solarsystem_id'])
            self.tmpl.assign('SSO_SOLARSYSTEM_NAME', cherrypy.session['sso_solarsystem_name'])
        # this can be used in any page showing header.html, so set it here
        self.tmpl.assign('last_visited_systems', list())  # empty list
        # TODO: self.fill_last_visited_systems()
        # this can be used in every page with zkb_block, so set it here
        self.tmpl.assign('zkb_block_title', '')
        self.setup_locale()

    def setup_locale(self):
        selected_locale = self.get_selected_locale_code()
        self.tmpl.assign('LOCALE', selected_locale)
        self.tmpl.assign('SUPPORTED_LOCALES', self.tr.supported_locales)
        self.tmpl.assign('tr', self.tr.get_translator(selected_locale))

    def postprocess_zkb_kills(self, kills: list) -> list:
        """
        Add some EXTRA information to kills list provided by ZKillboard API
        Adds type names and extra solarsystem info
        :param kills: list of kills as provided by zkillboard
        :return: modified list
        """
        try:
            for a_kill in kills:
                # find type name for victim ship
                type_info = self.db.find_typeid(a_kill['victim']['shipTypeID'])
                a_kill['victim']['shipTypeName'] = type_info['name']
                a_kill['victim']['shipGroupName'] = type_info['groupname']
                a_kill['our_corp'] = ''
                # victim_corpid = a_kill['victim']['corporationID']
                # if self.siteconfig.is_our_corp(victim_corpid):
                #     a_kill['our_corp'] = 'loss'  # victim is our corp
                # go through all attackers
                for atk in a_kill['attackers']:
                    # find type name for attacker ship
                    type_info = self.db.find_typeid(atk['shipTypeID'])
                    atk['shipTypeName'] = type_info['name']
                    # look for our corp kills/losses
                    # if self.cfg.is_our_corp(atk['corporationID']):
                    #    if a_kill['our_corp'] == '':
                    #        a_kill['our_corp'] = 'kill'
                # find solarsystem name for solarsystem id
                a_kill['solarSystemName'] = ''
                a_kill['solarSystemRegion'] = ''
                a_kill['solarSystemSecurity'] = 0.0
                a_kill['solarSystemSecurityColor'] = '#FFFFFF'
                a_kill['solarSystemWhClass'] = ''
                ss_info = self.db.find_ss_by_id(a_kill['solarSystemID'])
                if ss_info is not None:
                    a_kill['solarSystemName'] = ss_info['name']
                    a_kill['solarSystemRegion'] = ss_info['regionname']
                    a_kill['solarSystemSecurity'] = ss_info['security']
                    a_kill['solarSystemSecurityColor'] = get_ss_security_color(ss_info['security'])
                whsys_row = self.db.query_wormholesystem_new(a_kill['solarSystemID'])
                if whsys_row is not None:
                    a_kill['solarSystemWhClass'] = WHClass.to_string(int(whsys_row[0]))
            # resolve characters, corporations, alliances names from their IDs
            kills = self.names_db.fill_names_in_zkb_kills(kills)
        except KeyError as k_e:
            self.debuglog('ZKB API changed (again), it was a KeyError: {}'.format(str(k_e)))
        return kills

    @cherrypy.expose()
    def index(self):
        self.init_session()
        self.setup_template_vars('index')

        # ZKB stuff removed, async AJAX loader will be used instead
        #zkb = ZKB(self.zkb_options)
        #zkb.add_wspace()

        # zkb.add_limit(30) # Zkillboard has disabled 'limit' parameter for all users:
        # '{"error":"Due to abuse of the limit parameter to avoid caches
        #  the ability to modify limit has been revoked for all users"}'
        #wspace_kills = zkb.go()
        #wspace_kills = self.postprocess_zkb_kills(wspace_kills)

        #self.tmpl.assign('zkb_kills', wspace_kills)
        #self.tmpl.assign('zkb_block_title', 'W-Space kills')
        #self.tmpl.assign('dbg_wspace_kills', dump_object(wspace_kills))
        #
        return self.tmpl.render('index.html')

    @cherrypy.expose()
    def effects(self):
        self.init_session()
        self.setup_template_vars('effects')
        translator = self.tr.get_translator(self.get_selected_locale_code())
        effs = self.db.select_all_effects()
        self.tmpl.assign('effects', effs)
        self.tmpl.assign('title', translator.gettext('Effects') + ' - WHDBX')
        return self.tmpl.render('effects.html')

    @cherrypy.expose()
    def sleepers(self, **params):
        self.init_session()
        self.setup_template_vars('sleepers')
        translator = self.tr.get_translator(self.get_selected_locale_code())
        sleeper = WHSleeper()
        self.tmpl.assign('sleeper', sleeper)
        if 'id' in params:
            sleeper_id = int(params['id'])
            sleeper.load_info(sleeper_id, self.db)
            self.tmpl.assign('MODE', 'single_sleeper')
            self.tmpl.assign('title', sleeper.name + ' - WHDBX')
            self.tmpl.assign('class_sleepers', self.db.query_sleeper_by_class(sleeper.wh_class_str))
            self.tmpl.assign('sleepers_c12', list())
            self.tmpl.assign('sleepers_c34', list())
            self.tmpl.assign('sleepers_c56', list())
        else:
            self.tmpl.assign('title', translator.gettext('Sleepers') + ' - WHDBX')
            self.tmpl.assign('class_sleepers', list())
            self.tmpl.assign('sleepers_c12', self.db.query_sleeper_by_class('1,2'))
            self.tmpl.assign('sleepers_c34', self.db.query_sleeper_by_class('3,4'))
            self.tmpl.assign('sleepers_c56', self.db.query_sleeper_by_class('5,6'))
        return self.tmpl.render('sleeper.html')

    @cherrypy.expose()
    def signatures(self, **params):
        self.init_session()
        self.setup_template_vars('signatures')
        translator = self.tr.get_translator(self.get_selected_locale_code())
        self.tmpl.assign('title', translator.gettext('Signatures') + ' - WHDBX')
        #
        sig_id = -1
        if 'id' in params:
            try:
                sig_id = int(params['id'])
            except ValueError:
                sig_id = -1
        # default vars
        sig = WHSignature(self.cfg)
        self.tmpl.assign('sig', sig)
        self.tmpl.assign('sig_dbg', None)
        self.tmpl.assign('sigs', list())
        # params
        if sig_id > 0:
            sig.load(sig_id, self.db)
            if sig.is_valid():
                self.tmpl.assign('title', sig.name + ' - WHDBX')
                self.tmpl.assign('MODE', 'single_signature')
                if sig.wh_class != 0:
                    self.tmpl.assign('sigs', self.db.query_signatures_for_class(sig.wh_class, True))
                if sig.wh_class == 0:  # ore site or gas site
                    if sig.sig_type == 'gas':
                        self.tmpl.assign('sigs', self.db.query_gas_signatures(True))
                    elif sig.sig_type == 'ore':
                        self.tmpl.assign('sigs', self.db.query_ore_signatures(True))
            self.tmpl.assign('sigs_c1', list())
            self.tmpl.assign('sigs_c2', list())
            self.tmpl.assign('sigs_c3', list())
            self.tmpl.assign('sigs_c4', list())
            self.tmpl.assign('sigs_c5', list())
            self.tmpl.assign('sigs_c6', list())
            self.tmpl.assign('sigs_gas', list())
            self.tmpl.assign('sigs_ore', list())
            self.tmpl.assign('sigs_thera', list())
        else:
            self.tmpl.assign('sigs_c1', self.db.query_signatures_for_class(1, True))
            self.tmpl.assign('sigs_c2', self.db.query_signatures_for_class(2, True))
            self.tmpl.assign('sigs_c3', self.db.query_signatures_for_class(3, True))
            self.tmpl.assign('sigs_c4', self.db.query_signatures_for_class(4, True))
            self.tmpl.assign('sigs_c5', self.db.query_signatures_for_class(5, True))
            self.tmpl.assign('sigs_c6', self.db.query_signatures_for_class(6, True))
            self.tmpl.assign('sigs_gas', self.db.query_gas_signatures(True))
            self.tmpl.assign('sigs_ore', self.db.query_ore_signatures(True))
            self.tmpl.assign('sigs_thera', self.db.query_signatures_for_class(WHClass.THERA_WH_CLASS, True))
        # debug mode
        if self.cfg.DEBUG:
            self.tmpl.assign('sig_dbg', dump_object(sig))
        return self.tmpl.render('signature.html')

    @cherrypy.expose()
    def whdb(self):
        self.init_session()
        self.setup_template_vars('whdb')
        translator = self.tr.get_translator(self.get_selected_locale_code())
        self.tmpl.assign('title', translator.gettext('WH Database') +  ' - WHDBX')
        return self.tmpl.render('whdb.html')

    @cherrypy.expose()
    def about(self):
        self.init_session()
        self.setup_template_vars('about')
        selected_locale = self.get_selected_locale_code()
        tr = self.tr.get_translator(selected_locale)
        self.tmpl.assign('title', tr.gettext('About project') + ' - WHDBX')
        return self.tmpl.render('about_' + selected_locale + '.html')

    @cherrypy.expose()
    def eve_sso_help(self):
        self.init_session()
        self.setup_template_vars('eve_sso_help')
        selected_locale = self.get_selected_locale_code()
        tr = self.tr.get_translator(selected_locale)
        self.tmpl.assign('title', tr.gettext('About EVE-SSO') + ' - WHDBX')
        return self.tmpl.render('eve_sso_help_' + selected_locale + '.html')

    @cherrypy.expose()
    def logout(self):
        # clear session
        self.sso_session_cleanup()
        # Redirect to index
        raise cherrypy.HTTPRedirect('/', status=302)
        return 'Redirecting...'  # never executed

    @cherrypy.expose()
    def ss(self, jsystem):
        self.init_session()
        self.setup_template_vars('ss')
        #
        # find solarsystem
        ss_info = self.db.find_ss_by_name(jsystem)
        if ss_info is None:
            return self.display_failure('Solar system not found: {}'.format(jsystem))
        ssid = ss_info['id']
        #
        # find whsystem
        whsys = WHSystem(self.db)
        whsys.query_info(ssid)
        if whsys.name != '':
            self.tmpl.assign('title', whsys.name + ' - WHDBX')
            # whsys.query_trade_routes(self.cfg)
            # ^^ With Eve-Central dead, we have no easy way to get trade routes
        #
        # WH signatures
        sigs = []
        if whsys.is_wh:
            sigs = self.db.query_signatures_for_class(whsys.wh_class, True)
        #
        # assign template vars
        self.tmpl.assign('whsys', whsys)
        self.tmpl.assign('utcnow', datetime.datetime.utcnow())
        self.tmpl.assign('sigs', sigs)
        if self.cfg.DEBUG:
            self.tmpl.assign('whsys_dbg', dump_object(whsys))
        return self.tmpl.render('whsystem_info.html')

    @cherrypy.expose()
    def eve_sso_callback(self, code, state):
        self.init_session()
        self.tmpl.unassign_all()

        # verify that saved state == received state
        saved_state = cherrypy.session.get('sso_state')
        if saved_state != state:
            return self.display_failure('Error in EVE-SSO Auth: invalid state!')

        # s = 'code=' + code + ' state=' + state
        # Now we have an auth code, it's time to obtain an access token.
        # the authorization code is single use only.

        try:
            r = requests.post('https://login.eveonline.com/oauth/token',
                              auth=(self.cfg.SSO_CLIENT_ID, self.cfg.SSO_SECRET_KEY),
                              headers={
                                  'Content-Type': 'application/x-www-form-urlencoded',
                                  'User-Agent': self.cfg.SSO_USER_AGENT
                              },
                              data={'grant_type': 'authorization_code', 'code': code},
                              timeout=10)
        except requests.exceptions.RequestException as req_e:
            return self.display_failure('Error during communication to '
                                        'login.eveonline.com (get token): <br />' + str(req_e))

        # {"access_token":"kumuk...LAnz4RJZA2","token_type":"Bearer","expires_in":1200,
        #  "refresh_token":"MkMi5cGg...fIQisV0"}

        try:
            details = json.loads(r.text)
        except json.JSONDecodeError:
            return self.display_failure('Error decoding server response '
                                        'from login.eveonline.com! (get token)')

        access_token = details['access_token']
        refresh_token = details['refresh_token']
        expires_in = int(details['expires_in'])
        td = datetime.timedelta(seconds=expires_in)
        dt_now = datetime.datetime.now()
        dt_utcnow = datetime.datetime.utcnow()
        dt_expire = dt_now + td
        dt_utcexpire = dt_utcnow + td

        # save those in session
        cherrypy.session['sso_token'] = access_token
        cherrypy.session['sso_refresh_token'] = refresh_token
        cherrypy.session['sso_expire_dt'] = dt_expire
        cherrypy.session['sso_expire_dt_utc'] = dt_utcexpire

        # obtain character ID and name
        try:
            # special request to EVE-SSO login site to get char ID & name (not part of OAuth2 protocol)
            # see http://eveonline-third-party-documentation.readthedocs.io/en/latest/sso/obtaincharacterid.html
            r = requests.get('https://login.eveonline.com/oauth/verify',
                             headers={
                                 'Authorization': 'Bearer ' + access_token,
                                 'User-Agent': self.cfg.SSO_USER_AGENT
                             },
                             timeout=10)
        except requests.exceptions.RequestException as req_e:
            return self.display_failure('Error during communication to '
                                        'login.eveonline.com (get character info): <br />' + str(req_e))
        response_text = r.text
        try:
            details = json.loads(response_text)
        except json.JSONDecodeError:
            return self.display_failure('Error decoding server response '
                                        'from login.eveonline.com! (get character info)')
        # store in session
        cherrypy.session['sso_char_id'] = str(details['CharacterID'])
        cherrypy.session['sso_char_name'] = str(details['CharacterName'])

        # Redirect to index
        raise cherrypy.HTTPRedirect('/', status=302)
        return 'Redirecting...'

    @cherrypy.expose()
    def ajax(self, **params):
        ret_print = ''  # this string will be returned as result
        if 'search_jsystem' in params:
            # this AJAX call that returns simple string; others return JSON strings.
            ret_print = self.ajax_search_jsystem(**params)
        elif 'search_hole_v2' in params:
            ret_print = self.ajax_search_hole_v2(**params)
        elif 'set_language' in params:
            ret_print = self.ajax_set_language(**params)
        elif 'whdb' in params:
            res = self.ajax_whdb_query(**params)
            ret_print = json.dumps(res)
        elif 'sso_refresh_token' in params:
            res = self.ajax_sso_call_refresh_token()
            ret_print = json.dumps(res)
        elif 'esi_call' in params:
            res = {'error': 'Unknown esi_call!'}
            call_type = str(params['esi_call'])
            if call_type == 'public_data':
                res = self.ajax_esi_call_public_data()
            elif call_type == 'location_ship':
                res = self.ajax_esi_call_location_ship()
            elif call_type == 'location_online':
                res = self.ajax_esi_call_location_online()
            elif call_type == 'location':
                res = self.ajax_esi_call_location_location()
            elif call_type == 'ui_open_window_information':
                if 'target_id' in params:
                    target_id = int(params['target_id'])
                    res = self.ajax_esi_call_ui_open_window_information(target_id)
            ret_print = json.dumps(res)
        elif 'zkb_block' in params:
            ret_print = self.ajax_zkb_block(**params)
        return ret_print

    def ajax_search_jsystem(self, **params) -> str:
        """
        params: search_jsystem - solarsystem name, like 'j170122' or 'J170122'
        This AJAX handler only checks that 'search_jsystem' exists.
        If it exists, it returns solarsystem name. 'ERROR' otherwise
        """
        ret = 'ERROR'  # default return
        search_jsystem = str(params['search_jsystem'])
        if is_whsystem_name(search_jsystem):
            jsys = self.db.find_ss_by_name(search_jsystem)
            if jsys:
                # solarsystem was found, return its name
                search_jsystem = search_jsystem.upper()
                # ret = str(jsys['id'])
                ret = search_jsystem
        return ret

    def ajax_search_hole_v2(self, **params) -> str:
        # init locale translator
        selected_locale = self.get_selected_locale_code()
        tr = self.tr.get_translator(selected_locale)
        ret = tr.gettext('Not found!')
        # actually search hole
        hole_name = str(params['search_hole_v2'])
        if hole_name != '':
            hole_name = hole_name.upper()
            wh = self.db.find_wormhole(hole_name)
            if wh is not None:
                wh['in_class_str'] = ''
                if wh['in_class'] != 0:
                    if wh['in_class'] == WHClass.THERA_WH_CLASS:
                        wh['in_class_str'] = 'Thera'
                    if wh['in_class'] == WHClass.FRIG_WH_CLASS:
                        wh['in_class_str'] = 'frig-WH'
                    if wh['in_class'] == WHClass.HISEC_WH_CLASS:
                        wh['in_class_str'] = 'High sec'
                    if wh['in_class'] == WHClass.LOW_WH_CLASS:
                        wh['in_class_str'] = 'Low sec'
                    if wh['in_class'] == WHClass.NULL_WH_CLASS:
                        wh['in_class_str'] = 'Null sec'
                    if (wh['in_class'] >= 1) and (wh['in_class'] <= 6):
                        wh['in_class_str'] = 'C' + str(wh['in_class'])
                    if (wh['in_class'] >= -6) and (wh['in_class'] <= -1):
                        wh['in_class_str'] = 'C' + str(wh['in_class']) + ' shattered'
                    if WHClass.is_drifters(wh['in_class']):
                        wh['in_class_str'] = 'Drifters WH'
                # create reply
                tip_str = ''
                # mass
                tip_str += tr.gettext('Mass:') + ' <b>'
                tip_str += str(int(wh['maxStableMass'] / 1000000))
                tip_str += '</b>  ' + tr.gettext('mil.kg') + '<br />'
                # jump mass
                tip_str += tr.gettext('Jump mass:') + ' <b>'
                tip_str += str(int(wh['maxJumpMass'] / 1000000))
                tip_str += '</b>  ' + tr.gettext('mil.kg') + '<br />'
                # lifetime
                tip_str += tr.gettext('Life time:') + ' <b>'
                tip_str += str(int(wh['maxStableTime'] / 60))
                tip_str += '</b>  ' + tr.gettext('hr.') + '<br />'
                # element code
                ret = '<span class=\"static_name\" onmouseover=\"Tip(\''
                ret += tip_str
                ret += '\');\" onmouseout=\"UnTip();\">'
                ret += wh['name'] + ' ' + wh['in_class_str'];
                ret += '</span>'
        return ret

    def ajax_set_language(self, **params) -> str:
        newlang = str(params['set_language'])
        newlang = newlang[0:2]  # 2-letter code
        if newlang in self.tr.supported_locales:
            cherrypy.session['configured_locale'] = newlang
            return 'OK'
        return 'ERROR: Unsupported locale'

    def ajax_whdb_query(self, **params) -> dict:
        # QUERY_PARAMS= {'whdb': ['1'], 'class': ['5', '6', 'shattered', 'frigwr']}
        res = dict()
        res['systems'] = []
        s3conn = self.db.connection_handle()
        q = 'SELECT solarsystemid, system, class, star, planets, moons, effect, statics \n'
        q += ' FROM wormholesystems_new'
        class_cond = ''
        eff_cond = ''
        static_cond = ''

        if 'class' in params:
            class_list = params['class']  # it can be single value, str...
            if type(class_list) == str:
                class_list = [class_list]
            for class_str in class_list:
                # first, optionally append " OR " to sql query
                if len(class_cond) > 0:
                    class_cond += ' OR '
                # determine if class_str is integer
                iclass = 0
                try:
                    iclass = int(class_str)
                except ValueError:
                    pass
                if iclass != 0:
                    # for all numeric classes, 1, 2, 3, -1, -2, -3, ...
                    class_cond += ('(class=' + str(iclass) + ')')
                else:
                    # special cases for string specifiers
                    if class_str == 'frigwr':
                        class_cond += '(class=13)'
                    elif class_str == 'drifters':
                        # drifters WH have several classes: 14, 15, 16, 17, 18
                        class_cond += '((class >= 14) AND (class <= 18))'
        if 'effect' in params:
            eff_list = params['effect']
            if type(eff_list) == str:
                eff_list = [eff_list]
            for eff in eff_list:
                if len(eff_cond) > 0:
                    eff_cond += ' OR '
                if eff == 'noeffect':
                    eff_cond += '(effect IS NULL)'
                elif eff == 'bh':
                    eff_cond += '(effect=\'Black Hole\')'
                elif eff == 'cv':
                    eff_cond += '(effect=\'Cataclysmic Variable\')'
                elif eff == 'mag':
                    eff_cond += '(effect=\'Magnetar\')'
                elif eff == 'pul':
                    eff_cond += '(effect=\'Pulsar\')'
                elif eff == 'rg':
                    eff_cond += '(effect=\'Red Giant\')'
                elif eff == 'wr':
                    eff_cond += '(effect=\'Wolf-Rayet Star\')'
        if 'in_class' in params:
            in_class_list = params['in_class']
            icl = ''
            for ic in in_class_list:
                if ic.isnumeric():
                    if icl != '':
                        icl += ' OR '
                    icl += ('in_class=' + ic)
            if icl != '':
                q2 = 'SELECT hole FROM wormholeclassifications WHERE '
                q2 += icl
                hole_list = []
                cur2 = s3conn.cursor()
                cur2.execute(q2)
                for row in cur2:
                    hole_list.append(row[0])
                    if static_cond != '':
                        static_cond += ' OR '
                    static_cond += '(statics LIKE \'%' + row[0] + '%\')'
        # finalize query
        where_cond = ''
        if class_cond != '':
            where_cond += '(' + class_cond + ')'
        if eff_cond != '':
            if where_cond != '':
                where_cond += ' AND '
            where_cond += '(' + eff_cond + ')'
        if static_cond != '':
            if where_cond != '':
                where_cond += ' AND '
            where_cond += '(' + static_cond + ')'
        if where_cond != '':
            q += '\n WHERE ' + where_cond

        self.debuglog('whdb: query:' + q)

        cursor = s3conn.cursor()
        cursor.execute(q)
        for row in cursor:
            jsys = dict()
            # solarsystemid, system, class, star, planets, moons, effect, statics
            jsys['id'] = int(row[0])
            jsys['name'] = row[1]
            jsys['class'] = int(row[2])
            jsys['star'] = row[3]  # not very needed
            jsys['planets'] = int(row[4])  # not very needed
            jsys['moons'] = int(row[5])  # not very needed
            jsys['effect'] = row[6]
            jsys['statics'] = []
            for st in str(row[7]).split(','):
                jsys['statics'].append(st)
            res['systems'].append(jsys)
        res['query'] = q
        cursor.close()

        # also fetch statics destinations classes
        for jsys in res['systems']:
            for i in range(0, len(jsys['statics'])):
                st_name = jsys['statics'][i]
                cursor = s3conn.cursor()
                q = 'SELECT in_class FROM wormholeclassifications WHERE hole = ?'
                cursor.execute(q, (st_name, ))
                row = cursor.fetchone()
                if row:
                    st_spec = '{} {}'.format(st_name, WHClass.to_string(row[0]))
                    jsys['statics'][i] = st_spec
                cursor.close()

        return res

    def ajax_sso_call_refresh_token(self) -> dict:
        self.debuglog('ajax: sso_refresh_token: start refresh')
        res = {
            'error': '',
            'sso_expire_dt_utc': ''
        }
        refresh_token = cherrypy.session['sso_refresh_token']
        if refresh_token == '':
            res['error'] = 'Not found refresh_token in saved session!'
            return res

        res = esi_calls.do_refresh_token(self.cfg, refresh_token)
        if res['error'] != '':
            self.debuglog('ajax: sso_refresh_token: error during refresh!')
            self.debuglog('      error: ' + res['error'])
            self.sso_session_cleanup()
            return res

        self.debuglog('ajax: sso_refresh_token: success')
        # save tokens in session
        cherrypy.session['sso_token']          = res['del']['sso_token']
        cherrypy.session['sso_refresh_token'] = res['del']['sso_refresh_token']
        cherrypy.session['sso_expire_dt']     = res['del']['sso_expire_dt']
        cherrypy.session['sso_expire_dt_utc'] = res['del']['sso_expire_dt_utc']
        del res['del']  # these values should not go exposed
        return res

    def ajax_esi_call_public_data(self) -> dict:
        self.debuglog('ajax: esi_call_public_data: start')
        # AJAX JSON return structure
        ret = {
            'error': '', # if this member is not an empty string, other fields are ignored
            'char_id': 0,
            'char_name': '',
            'corp_id': 0,
            'corp_name': '',
            'corp_ticker': '',
            'corp_member_count': 0,
            'ally_id': 0
        }
        if 'sso_char_id' not in cherrypy.session:
            ret['error'] = 'sso_char_id is not defined in session!'
            return ret
        if 'sso_char_name' not in cherrypy.session:
            ret['error'] = 'sso_char_name is not defined in session!'
            return ret
        # read session data
        char_id = cherrypy.session['sso_char_id']
        ret = esi_calls.public_data(self.cfg, char_id)
        if ret['error'] == '':
            # no error, ok, update session data
            cherrypy.session['sso_corp_id'] = ret['corp_id']
            cherrypy.session['sso_corp_name'] = ret['corp_name']
            cherrypy.session['sso_ally_id'] = ret['ally_id']
            self.debuglog('ajax: esi_call_public_data: success')
        else:
            self.debuglog('ajax: esi_call_public_data: error:' + ret['error'])
        return ret

    def ajax_esi_call_location_ship(self) -> dict:
        self.debuglog('ajax: ajax_esi_call_location_ship: start')
        ret = {
            'error': '',
            'ship_name': '',
            'ship_type_id': 0,
            'ship_type_name': ''
        }
        if 'sso_char_id' not in cherrypy.session:
            ret['error'] = 'sso_char_id is not defined in session!'
            return ret
        # This is an authenticated call; check if we have an access token
        if 'sso_token' not in cherrypy.session:
            ret['error'] = 'SSO access_token is not defined in session!'
            return ret
        char_id = cherrypy.session['sso_char_id']
        access_token = cherrypy.session['sso_token']
        ret = esi_calls.location_ship(self.cfg, char_id, access_token)
        if ret['error'] != '':
            self.debuglog('ajax: ajax_esi_call_location_ship: error:' + ret['error'])
            return ret
        typeinfo = self.db.find_typeid(ret['ship_type_id'])
        if typeinfo is not None:
            ret['ship_type_name'] = typeinfo['name']
        cherrypy.session['sso_ship_id'] = ret['ship_type_id']
        cherrypy.session['sso_ship_name'] = ret['ship_type_name']
        cherrypy.session['sso_ship_title'] = ret['ship_name']
        self.debuglog('ajax: ajax_esi_call_location_ship: success')
        return ret

    def ajax_esi_call_location_online(self) -> dict:
        self.debuglog('ajax: ajax_esi_call_location_online: start')
        ret = {
            'error': '',
            'is_online': False,
            'online': False,
            'logins': 0,
        }
        if 'sso_char_id' not in cherrypy.session:
            ret['error'] = 'sso_char_id is not defined in session!'
            return ret
        # This is an authenticated call; check if we have an access token
        if 'sso_token' not in cherrypy.session:
            ret['error'] = 'SSO access_token is not defined in session!'
            return ret
        char_id = cherrypy.session['sso_char_id']
        access_token = cherrypy.session['sso_token']
        ret = esi_calls.location_online(self.cfg, char_id, access_token)
        if ret['error'] == '':
            self.debuglog('ajax: ajax_esi_call_location_online: success')
            if 'online' in ret:
                ret['is_online'] = ret['online']
        else:
            self.debuglog('ajax: ajax_esi_call_location_online: error: ' + ret['error'])
        return ret

    def ajax_esi_call_location_location(self) -> dict:
        self.debuglog('ajax: ajax_esi_call_location_location: start')
        ret = {
            'error': '',
            'solarsystem_id': 0,
            'solarsystem_name': '',
            'is_whsystem': False,
            'is_docked': False,
            'structure_id': 0,
            'station_id': 0
        }
        if 'sso_char_id' not in cherrypy.session:
            ret['error'] = 'sso_char_id is not defined in session!'
            return ret
        # This is an authenticated call; check if we have an access token
        if 'sso_token' not in cherrypy.session:
            ret['error'] = 'SSO access_token is not defined in session!'
            return ret
        char_id = cherrypy.session['sso_char_id']
        access_token = cherrypy.session['sso_token']

        ret = esi_calls.location_location(self.cfg, char_id, access_token)
        if ret['error'] != '':
            self.debuglog('ajax: ajax_esi_call_location_location: error' + ret['error'])
            return ret

        ss_info = self.db.find_ss_by_id(ret['solarsystem_id'])
        if ss_info is not None:
            ret['solarsystem_name'] = ss_info['name']
            if is_whsystem_name(ret['solarsystem_name']):
                ret['is_whsystem'] = True
        # save in session
        cherrypy.session['sso_solarsystem_id'] = ret['solarsystem_id']
        cherrypy.session['sso_solarsystem_name'] = ret['solarsystem_name']
        self.debuglog('ajax: ajax_esi_call_location_location: success')
        return ret

    def ajax_esi_call_ui_open_window_information(self, target_id: int) -> dict:
        self.debuglog('ajax: ajax_esi_call_ui_open_window_information: {} start'.format(target_id))
        ret = {
            'error': ''
        }
        if not 'sso_token' in cherrypy.session:
            ret['error'] = 'SSO access_token is not defined in session!'
            return ret
        access_token = cherrypy.session['sso_token']
        try:
            result = esi_calls.ui_open_window_information(self.cfg, target_id, access_token)
            if result == False:
                ret['error'] = 'open window information: Request failed!'
        except esi_calls.ESIException as ex:
            ret['error'] = ex.error_string()
        if ret['error'] == '':
            self.debuglog('ajax: ajax_esi_call_ui_open_window_information: success')
        else:
            self.debuglog('ajax: ajax_esi_call_ui_open_window_information: error: {}'.format(ret['error']))
        return ret

    def ajax_zkb_block(self, **params) -> str:
        # return ready-to-render HTML block
        ssid = str(params['ssid'])
        # common init
        self.init_session()
        self.setup_template_vars('zkb_block')
        # ZKB
        zkb = ZKB(self.zkb_options)
        if ssid == 'w-space':
            zkb.add_wspace()
            self.tmpl.assign('zkb_block_title', 'W-Space kills')
        else:
            zkb.add_solarSystem(int(ssid))
            self.tmpl.assign('zkb_block_title', '')
        # zkb.add_limit(30) # Zkillboard has disabled 'limit' parameter for all users:
        # '{"error":"Due to abuse of the limit parameter to avoid caches
        #  the ability to modify limit has been revoked for all users"}'
        zkb_kills = zkb.go()
        zkb_kills = self.postprocess_zkb_kills(zkb_kills)
        self.tmpl.assign('zkb_kills', zkb_kills)
        #
        return self.tmpl.render('zkb_block.html')


if __name__ == '__main__':
    # maybe we have some command-line arguments?
    ap = argparse.ArgumentParser(description='WHDBX web application launcher',
                                 add_help=True, allow_abbrev=False)
    ap.add_argument('--host', action='store', default='127.0.0.1', type=str, metavar='BIND_HOST',
                    help='Host to bind to. Default: 127.0.0.1')
    ap.add_argument('--port', action='store', default='8081', type=int, metavar='BIND_PORT',
                    help='Port to listen on. Default: 8081')
    ap.add_argument('--autoreload', action='store_true', default=False,
                    help='Enable cherrypy autoreload function. It self-restarts the server'
                         ' if source files are changed.')
    args = ap.parse_args()

    cherrypy.config.update({
        'server.socket_host': args.host,
        'server.socket_port': args.port,
        'engine.autoreload.on': args.autoreload,
        'log.screen': False
    })

    # proxies = {
    #   'http': 'http://user:pass@10.10.1.10:3128/',
    #   'https': 'http://10.10.1.10:1080',
    # }
    #esi_calls.set_esi_proxies({'http': 'http://user:pass@eve-wh.space:8080/',
    #                           'https': 'http://user:pass@eve-wh.space:8080/'})

    whdbx_app = WhdbxApp()
    cherrypy.tree.mount(whdbx_app, '/', whdbx_app.get_cherrypy_app_config())

    # handle console Ctrl+C events
    cherrypy.engine.signals.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
