#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import json
import datetime
import os
import os.path
import pathlib

import cherrypy
from cherrypy._cpdispatch import Dispatcher

from classes.sitecfg import SiteConfig
from classes.template_engine import TemplateEngine


class WhdbxCustomDispatcher(Dispatcher):
    def __call__(self, path_info: str):
        path_info = path_info.lower()
        return Dispatcher.__call__(self, path_info)


class WhdbxMain:
    def __init__(self):
        p = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
        self.rootdir = p.as_posix()
        self.cfg = SiteConfig()
        self.tmpl = TemplateEngine(self.cfg)
        cherrypy.log('Whdbx started, rootdir=[{}]'.format(self.rootdir))

    def debugprint(self) -> str:
        res = ''
        cherrypy.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        res += 'use evekill: ' + str(self.cfg.ZKB_USE_EVEKILL)
        res += str(os.environ)
        return res

    # call this if any input error
    def display_failure(self, comment: str = None) -> str:
        if comment:
            self.tmpl.assign('error_comment', comment)
        res = self.tmpl.render('header.html')
        res += self.tmpl.render('failure.html')
        res += self.tmpl.render('footer.html')
        return res

    def setup_template_vars(self, page: str = ''):
        self.tmpl.unassign_all()
        self.tmpl.assign('title', 'WHDBX')
        self.tmpl.assign('error_comment', '')  # should be always defined!
        self.tmpl.assign('MODE', page)
        self.tmpl.assign('sitecfg', self.cfg)
        if self.cfg.EMULATE:
            self.tmpl.assign('URL_APPEND_EMULATE', '&amp;EMULATE=1')
        else:
            self.tmpl.assign('URL_APPEND_EMULATE', '')
        # TODO: assign crest data
        self.tmpl.assign('HAVE_CREST', 'false')
        #self.tmpl.assign('char', self.igb.get_char())
        #self.tmpl.assign('ssys', self.igb.get_solarsystem())
        #self.tmpl.assign('corp', self.igb.get_corp())
        #self.tmpl.assign('ship', self.igb.get_ship())
        #self.tmpl.assign('station', self.igb.get_station())
        # this can be used in any page showing header.html, so set default it here
        self.tmpl.assign('last_visited_systems', list())  # empty list
        # TODO: self.fill_last_visited_systems()

    @cherrypy.expose()
    def index(self):
        self.setup_template_vars('index')
        return self.tmpl.render('index.html')


if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 81,
        'engine.autoreload.on': True
    })

    whdbx_config = {
        '/': {
            'request.dispatch': WhdbxCustomDispatcher(),
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
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
