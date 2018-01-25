import pathlib

import cherrypy

from .sitecfg import SiteConfig
from .template_engine import TemplateEngine
from .tr_support import MultiLangTranslator


def erro_page_detect_request_locale(tr: MultiLangTranslator) -> str:
    """
    Determine what locale to use to translate user-visible sstrings
    for *current* client request. Try to look for preconfigured value in
    session, or try to parse Accept-Language HTTP header. In case of
    no locale can be determined, or locale unsupported, return 'en'
    :return: string, 'en', 'ru', etc. Always returns valid value
    """
    selected_locale = 'en'
    # first, check that user has configured language. Then don't autodetect
    if 'configured_locale' in cherrypy.session:
        if cherrypy.session['configured_locale'] != '':
            configured_locale = cherrypy.session['configured_locale']
            if configured_locale in tr.supported_locales:
                selected_locale = configured_locale
    # no user-configured locale, try to autodetect
    accept_language = ''
    if 'accept-language' in cherrypy.request.headers:
        accept_language = cherrypy.request.headers['accept-language']
        accept_language = accept_language[0:2]
    if accept_language != '':
        selected_locale = accept_language
    return selected_locale


def error_page_create_template_engine(title: str, mode: str) -> TemplateEngine:
    siteconfig = SiteConfig()
    te = TemplateEngine(siteconfig)
    te.assign('title', title)  # default title
    te.assign('MODE', mode)  # current page identifier
    te.assign('sitecfg', siteconfig)
    te.assign('error_comment', '')  # should be always defined!
    # assign EVE-SSO data defaults
    te.assign('HAVE_SSO_LOGIN', False)
    te.assign('SSO_TOKEN_EXPIRE_DT', '')
    te.assign('SSO_LOGIN_URL', '')
    te.assign('SSO_CHAR_ID', '')
    te.assign('SSO_CHAR_NAME', '')
    te.assign('SSO_CORP_ID', '')
    te.assign('SSO_CORP_NAME', '')
    te.assign('SSO_SHIP_ID', '')
    te.assign('SSO_SHIP_NAME', '')
    te.assign('SSO_SHIP_TITLE', '')
    te.assign('SSO_SOLARSYSTEM_ID', '')
    te.assign('SSO_SOLARSYSTEM_NAME', '')
    te.assign('SSO_ONLINE', '')
    te.assign('last_visited_systems', list())  # empty list
    # setup locale
    locales_dir = pathlib.Path('./locales').resolve().as_posix()
    tr = MultiLangTranslator(locales_dir, 'whdbx')
    tr.init_translations()
    request_locale = erro_page_detect_request_locale(tr)
    te.assign('LOCALE', request_locale)
    te.assign('SUPPORTED_LOCALES', tr.supported_locales)
    te.assign('tr', tr.get_translator(request_locale))
    return te


def page_404(status, message, traceback, version):
    te = error_page_create_template_engine(title='404 - WHDBX', mode='error404')
    return te.render('404.html')


def page_500(status, message, traceback, version):
    te = error_page_create_template_engine(title='500 - WHDBX', mode='error500')
    te.assign('stacktrace', str(traceback))
    return te.render('500.html')
