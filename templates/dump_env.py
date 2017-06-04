## -*- coding: utf-8 -*-
<%
import os

context.write('<hr /><div class="dev_data_dump">')

env_ks = os.environ.keys()
for ev in env_ks:
    # first only 'HTTP_EVE' vars
    ev_s = ev[0:8]
    if ev_s == 'HTTP_EVE':
        context.write('[{0}] = [{1}]<br />'.format(ev, os.environ[ev]))
    # context.write('[{0}][{2}] = [{1}]<br />'.format(ev, os.environ[ev], ev_s))

context.write('<hr />')

for ev in env_ks:
    # then other vars
    ev_s = ev[0:8]
    if ev_s != 'HTTP_EVE':
        context.write('[{0}] = [{1}]<br />'.format(ev, os.environ[ev]))

context.write('</div><hr />')

%>