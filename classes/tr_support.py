import gettext
import pathlib
from typing import Optional


class MultiLangTranslator:
    def __init__(self, localesdir: str, domain=None):
        self.domain = 'whdbx'  # translation domain, for gettext
        if domain is not None:
            self.domain = domain
        self.localesdir = localesdir
        self.supported_locales = []
        self.translators = dict()

    def init_translations(self):
        p = pathlib.Path(self.localesdir)
        for sub_p in p.iterdir():
            if sub_p.is_dir():
                try:
                    # If no .mo file is found, this function
                    #    raises OSError if fallback is false
                    #  Changed in version 3.3: IOError used to
                    #    be raised instead of OSError.
                    translator = gettext.translation(
                        self.domain, localedir=self.localesdir,
                        languages=[sub_p.name], fallback=False)
                    # if we're here, translation loaded OK
                    self.supported_locales.append(sub_p.name)
                    self.translators[sub_p.name] = translator
                except IOError:
                    pass
        print(self.supported_locales)

    def get_translator(self, locale_name: str) -> Optional[gettext.GNUTranslations]:
        if locale_name in self.translators:
            return self.translators[locale_name]
        return None
