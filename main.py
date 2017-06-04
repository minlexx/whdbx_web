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

    @cherrypy.expose()
    def index(self):
        return 'index'


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
