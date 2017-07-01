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
from classes.database import SiteDb, WHClass, get_ss_security_color
from classes.sleeper import WHSleeper
from classes.signature import WHSignature
from classes.zkillboard import ZKB
from classes.whsystem import WHSystem
from classes.utils import dump_object, is_whsystem_name


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
        self.zkb_options = {
            'debug': self.cfg.DEBUG,
            'cache_time': self.cfg.ZKB_CACHE_TIME,
            'cache_type': self.cfg.ZKB_CACHE_TYPE,
            'cache_dir': self.cfg.ZKB_CACHE_DIR,
            'use_evekill': self.cfg.ZKB_USE_EVEKILL
        }
        cherrypy.log('started, rootdir=[{}]'.format(self.rootdir), 'WHDBXAPP')

    def debugprint(self, msg: str = '') -> str:
        res = ''
        cherrypy.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        res += 'use evekill: ' + str(self.cfg.ZKB_USE_EVEKILL) + '\n'
        res += str(os.environ) + '\n'
        res += msg
        return res

    # call this if any input error
    def display_failure(self, comment: str = '') -> str:
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
        self.tmpl.assign('zkb_block_title', '')

    def postprocess_zkb_kills(self, kills: list) -> list:
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
        return kills

    @cherrypy.expose()
    def index(self):
        self.init_session()
        self.setup_template_vars('index')
        # ZKB
        zkb = ZKB(self.zkb_options)
        zkb.add_wspace()
        zkb.add_limit(30)
        wspace_kills = zkb.go()
        wspace_kills = self.postprocess_zkb_kills(wspace_kills)
        self.tmpl.assign('zkb_kills', wspace_kills)
        self.tmpl.assign('zkb_block_title', 'W-Space kills')
        self.tmpl.assign('dbg_wspace_kills', dump_object(wspace_kills))
        #
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
    def whdb(self):
        self.init_session()
        self.setup_template_vars('whdb')
        self.tmpl.assign('title', 'База ВХ - WHDBX')
        return self.tmpl.render('whdb.html')

    @cherrypy.expose()
    def about(self):
        self.init_session()
        self.setup_template_vars('about')
        self.tmpl.assign('title', 'О проекте - WHDBX')
        return self.tmpl.render('about.html')

    @cherrypy.expose()
    def eve_sso_help(self):
        self.init_session()
        self.setup_template_vars('eve_sso_help')
        self.tmpl.assign('title', 'O EVE-SSO - WHDBX')
        return self.tmpl.render('eve_sso_help.html')

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
            whsys.query_trade_routes(self.cfg)
        #
        # zkillboard
        zkb = ZKB(self.zkb_options)
        zkb.add_solarSystem(ssid)
        zkb.add_limit(30)
        zkb_kills = zkb.go()
        zkb_kills = self.postprocess_zkb_kills(zkb_kills)
        #
        # WH signatures
        sigs = []
        if whsys.is_wh:
            sigs = self.db.query_signatures_for_class(whsys.wh_class)
        #
        # assign template vars
        self.tmpl.assign('whsys', whsys)
        self.tmpl.assign('zkb_kills', zkb_kills)
        self.tmpl.assign('zkb_block_title', '')
        self.tmpl.assign('utcnow', datetime.datetime.utcnow())
        self.tmpl.assign('sigs', sigs)
        if self.cfg.DEBUG:
            self.tmpl.assign('whsys_dbg', dump_object(whsys))
        # return self.debugprint('/ss: requested info about: {}'.format(jsystem))
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
        if 'whdb' in params:
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
                class_list = params['class']
                has_shattered = False
                for cd in class_list:
                    if cd.isnumeric():
                        if len(class_cond) > 0:
                            class_cond += ' OR '
                        class_cond += ('(class=' + str(cd) + ')')
                    elif cd == 'shattered':
                        has_shattered = True
                    elif cd == 'frigwr':
                        if len(class_cond) > 0:
                            class_cond += ' OR '
                        class_cond += '(class=13)'
                    elif cd == 'drifters':
                        if len(class_cond) > 0:
                            class_cond += ' OR '
                        class_cond += '((class >= 14) AND (class <= 18))'
                if has_shattered and (len(class_cond) > 0):
                    for cd in class_list:
                        if cd.isnumeric():
                            class_cond += ' OR '
                            class_cond += ('(class=-' + str(cd) + ')')
            if 'effect' in params:
                eff_list = params['effect']
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
            cursor = s3conn.cursor()
            cursor.execute(q)
            for row in cursor:
                jsys = dict()
                # solarsystemid, system, class, star, planets, moons, effect, statics
                jsys['id'] = int(row[0])
                jsys['name'] = row[1]
                jsys['class'] = int(row[2])
                # jsys['star'] = row[3]  # not very needed
                # jsys['planets'] = int(row[4])  # not very needed
                # jsys['moons'] = int(row[5])  # not very needed
                jsys['effect'] = row[6]
                jsys['statics'] = []
                for st in str(row[7]).split(','):
                    jsys['statics'].append(st)
                res['systems'].append(jsys)
            res['query'] = q
            # output result
            ret_print = json.dumps(res)
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
