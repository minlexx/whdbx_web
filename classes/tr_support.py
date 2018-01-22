import gettext

tr_support_global_translator = None


def get_translator(localedir: str = None) -> gettext.GNUTranslations:
    global tr_support_global_translator
    if tr_support_global_translator is None:
        tr_support_global_translator = gettext.translation(
            'whdbx', localedir=localedir, languages=['ru'], fallback=True)
    return tr_support_global_translator
