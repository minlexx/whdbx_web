#!/bin/bash
#pygettext3 -v --keyword=tr.gettext -d whdbx -n -o whdbx.po -p locales ./**.py
xgettext --keyword=tr.gettext -d whdbx -n -j -o whdbx.po -p locales ./*.py
xgettext --keyword=tr.gettext -d whdbx -n -j -o whdbx.po -p locales ./classes/*.py
xgettext --keyword=tr.gettext -d whdbx -n -j -o whdbx.po -p locales -L Python ./templates/*.html
