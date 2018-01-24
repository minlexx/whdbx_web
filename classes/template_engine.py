# -*- coding: utf-8 -*-

from . import sitecfg
from mako.lookup import TemplateLookup
from mako import exceptions


class TemplateEngine:
    def __init__(self, siteconfig: sitecfg.SiteConfig):
        params = {
            'directories':      siteconfig.TEMPLATE_DIR,
            'module_directory': siteconfig.TEMPLATE_CACHE_DIR,
            # 'input_encoding':   'utf-8',
            # 'output_encoding':   'utf-8',
            # 'encoding_errors':  'replace',
            'strict_undefined': True
        }
        self._lookup = TemplateLookup(**params)
        self._args = dict()
        self._headers_sent = False

    def assign(self, vname: str, vvalue):
        self._args[vname] = vvalue

    def is_set(self, vname: str) -> bool:
        if vname in self._args:
            return True
        return False

    def value(self, vname: str):
        if vname in self._args:
            return self._args[vname]
        return None

    def unassign(self, vname: str):
        if vname in self._args:
            self._args.pop(vname)

    def unassign_all(self):
        self._args = dict()

    def render(self, tname):
        tmpl = self._lookup.get_template(tname)
        return tmpl.render(**self._args)
        # return tmpl.render_unicode(**self._args)

    def output(self, tname):
        if not self._headers_sent:
            print('Content-Type: text/html')
            print()
            self._headers_sent = True
        # MAKO exceptions handler
        try:
            rendered = self.render(tname)
            print(rendered)  # python IO encoding mut be set to utf-8 (see ../main.py header for details)
            # print(os.environ)
            # print(locale.getpreferredencoding())
            # print(type(rendered))
            # print(rendered[0:1370])
            # part = rendered[1371:1374]
            # if 'LANG' in os.environ:
            #    print(os.environ['LANG'])
            # if 'LC_ALL' in os.environ:
            #    print(os.environ['LC_ALL'])
        except exceptions.MakoException:
            print(exceptions.html_error_template().render())
