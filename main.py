#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import json
import datetime
import os
import os.path
import pathlib
import re
import uuid

import cherrypy
from cherrypy._cpdispatch import Dispatcher
import requests
import requests.exceptions

from classes.sitecfg import SiteConfig
from classes.template_engine import TemplateEngine
from classes.database import SiteDb, WHClass
from classes.sleeper import WHSleeper
from classes.signature import WHSignature
from classes.utils import dump_object


def is_whsystem_name(name: str) -> bool:
    if name.lower() == 'thera': return True  # special case
    if len(name) != 7: return False  # must be 7 chars
    if name[0] not in ['j', 'J']: return False  # 1st letter should be j or J
    name = name[1:]  # other 6 characters must be numbers
    m = re.match(r'^[0123456789]+$', name)
    if m is None: return False
    return True


class WhdbxCustomDispatcher(Dispatcher):

    sleepers_id_match = re.compile(r'/sleepers/([0-9]+)/')
    signatures_id_match = re.compile(r'/signatures/([0-9]+)/')

    def __call__(self, path_info: str):
        path_info = path_info.lower()
        # check that requested path is in form 'J123456' ('/j170122')
        # redirects /J123456 to /ss/?jsystem=J123456
        if len(path_info) > 1:
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


class WhdbxMain:
    def __init__(self):
        self.rootdir = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).as_posix()
        self.cfg = SiteConfig()
        self.tmpl = TemplateEngine(self.cfg)
        self.db = SiteDb(self.cfg)
        cherrypy.log('Whdbx started, rootdir=[{}]'.format(self.rootdir))

    def debugprint(self, msg: str = '') -> str:
        res = ''
        cherrypy.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        res += 'use evekill: ' + str(self.cfg.ZKB_USE_EVEKILL) + '\n'
        res += str(os.environ) + '\n'
        res += msg
        return res

    # call this if any input error
    def display_failure(self, comment: str = None) -> str:
        if comment:
            self.tmpl.assign('error_comment', comment)
        return self.tmpl.render('failure.html')

    def init_session(self):
        # create all needed default values in session
        if 'sso_state' not in cherrypy.session:
            new_state = uuid.uuid4().hex
            cherrypy.session['sso_state'] = new_state
            cherrypy.log('Generated new sso_state = {}'.format(new_state))
        #
        needed_sso_vars = ['sso_token', 'sso_refresh_token', 'sso_expire_dt']
        for var_name in needed_sso_vars:
            if var_name not in cherrypy.session:
                cherrypy.session[var_name] = ''

    def setup_template_vars(self, page: str = ''):
        self.tmpl.unassign_all()
        self.tmpl.assign('title', 'WHDBX')
        self.tmpl.assign('error_comment', '')  # should be always defined!
        self.tmpl.assign('MODE', page)
        self.tmpl.assign('sitecfg', self.cfg)
        # TODO: assign crest data
        self.tmpl.assign('HAVE_SSO_LOGIN', 'false')
        self.tmpl.assign('SSO_LOGIN_URL', self.cfg.sso_login_url(cherrypy.session['sso_state']))
        self.tmpl.assign('char', {})
        self.tmpl.assign('ssys', {})
        self.tmpl.assign('corp', {})
        self.tmpl.assign('ship', {})
        self.tmpl.assign('station', {})
        # this can be used in any page showing header.html, so set default it here
        self.tmpl.assign('last_visited_systems', list())  # empty list
        # TODO: self.fill_last_visited_systems()

    @cherrypy.expose()
    def index(self):
        self.init_session()
        self.setup_template_vars('index')
        return self.tmpl.render('index.html')

    @cherrypy.expose()
    def effects(self):
        self.init_session()
        self.setup_template_vars('effects')
        effs = self.db.select_all_effects()
        self.tmpl.assign('effects', effs)
        self.tmpl.assign('title', 'Эффекты - WHDBX')
        return self.tmpl.render('effects.html')

    @cherrypy.expose()
    def sleepers(self, **params):
        self.init_session()
        self.setup_template_vars('sleepers')
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
            self.tmpl.assign('title', 'Слиперы - WHDBX')
            self.tmpl.assign('class_sleepers', list())
            self.tmpl.assign('sleepers_c12', self.db.query_sleeper_by_class('1,2'))
            self.tmpl.assign('sleepers_c34', self.db.query_sleeper_by_class('3,4'))
            self.tmpl.assign('sleepers_c56', self.db.query_sleeper_by_class('5,6'))
        return self.tmpl.render('sleeper.html')

    @cherrypy.expose()
    def signatures(self, **params):
        self.init_session()
        self.setup_template_vars('signatures')
        self.tmpl.assign('title', 'Сигнатурки - WHDBX')
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
                    self.tmpl.assign('sigs', self.db.query_signatures_for_class(sig.wh_class))
                if sig.wh_class == 0:  # ore site or gas site
                    if sig.sig_type == 'gas':
                        self.tmpl.assign('sigs', self.db.query_gas_signatures())
                    elif sig.sig_type == 'ore':
                        self.tmpl.assign('sigs', self.db.query_ore_signatures())
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
            self.tmpl.assign('sigs_c1', self.db.query_signatures_for_class(1))
            self.tmpl.assign('sigs_c2', self.db.query_signatures_for_class(2))
            self.tmpl.assign('sigs_c3', self.db.query_signatures_for_class(3))
            self.tmpl.assign('sigs_c4', self.db.query_signatures_for_class(4))
            self.tmpl.assign('sigs_c5', self.db.query_signatures_for_class(5))
            self.tmpl.assign('sigs_c6', self.db.query_signatures_for_class(6))
            self.tmpl.assign('sigs_gas', self.db.query_gas_signatures())
            self.tmpl.assign('sigs_ore', self.db.query_ore_signatures())
            self.tmpl.assign('sigs_thera', self.db.query_signatures_for_class(WHClass.THERA_WH_CLASS))
        # debug mode
        if self.cfg.DEBUG:
            self.tmpl.assign('sig_dbg', dump_object(sig))
        return self.tmpl.render('signature.html')

    @cherrypy.expose()
    def ss(self, jsystem):
        self.init_session()
        self.setup_template_vars('ss')
        return self.debugprint('/ss: requested info about: {}'.format(jsystem))

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
                              headers={'Content-Type': 'application/x-www-form-urlencoded'},
                              data={'grant_type': 'authorization_code', 'code': code},
                              timeout=10)
        except requests.exceptions.RequestException as req_e:
            return self.display_failure('Error during communication to '
                                        'login.eveonline.com: <br />' + str(req_e))

        # {"access_token":"kumuk...LAnz4RJZA2","token_type":"Bearer","expires_in":1200,
        #  "refresh_token":"MkMi5cGg...fIQisV0"}

        try:
            details = json.loads(r.text)
        except json.JSONDecodeError:
            return self.display_failure('Error decoding server response from login.eveonline.com!')

        access_token = details['access_token']
        refresh_token = details['refresh_token']
        expires_in = int(details['expires_in'])
        td = datetime.timedelta(seconds=expires_in)
        dt_now = datetime.datetime.now()
        dt_expire = dt_now + td

        # save those in session
        cherrypy.session['sso_token'] = access_token
        cherrypy.session['sso_refresh_token'] = refresh_token
        cherrypy.session['sso_expire_dt'] = dt_expire

        # Redirect to index
        raise cherrypy.HTTPRedirect('/', status=302)
        return 'Redirecting...'

    @cherrypy.expose()
    def ajax(self, **params):
        ret_print = 'ERROR'  # default return
        #
        if 'search_jsystem' in params:
            """
            params: search_jsystem - solarsystem name, like 'j170122' or 'J170122'
            This AJAX handler only checks that 'search_jsystem' exists.
            If it exists, it returns solarsystem name. 'ERROR' otherwise
            """
            search_jsystem = str(params['search_jsystem'])
            if is_whsystem_name(search_jsystem):
                jsys = self.db.find_ss_by_name(search_jsystem)
                if jsys:
                    # solarsystem was found, return its name
                    search_jsystem = search_jsystem.upper()
                    # ret_print = str(jsys['id'])
                    ret_print = search_jsystem
        #
        if 'search_hole' in params:
            hole_name = str(params['search_hole'])
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
                    ret_print = json.dumps(wh)
        return ret_print


if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 81,
        'engine.autoreload.on': True
    })

    rootdir = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).as_posix()

    whdbx_config = {
        '/': {
            'request.dispatch': WhdbxCustomDispatcher(),
            'tools.sessions.on': True,
            'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
            'tools.sessions.storage_path': rootdir + "/sessions",
            'tools.sessions.timeout': 30*24*3600,  # month
            'tools.staticdir.root': rootdir
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.tree.mount(WhdbxMain(), '/', whdbx_config)

    # handle console Ctrl+C events
    cherrypy.engine.signals.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
