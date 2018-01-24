@set XGETTEXT=.\tools\gettext-win32\xgettext.exe
%XGETTEXT% --keyword=tr.gettext -d whdbx -n -j -o whdbx.po -p locales .\*.py
%XGETTEXT% --keyword=tr.gettext -d whdbx -n -j -o whdbx.po -p locales .\classes\*.py
%XGETTEXT% --keyword=tr.gettext -d whdbx -n -j -o whdbx.po -p locales -L Python .\templates\*.html
pause
