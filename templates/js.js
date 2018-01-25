## -*- coding: utf-8 -*-
<%
from classes.utils import js_escape
%>

% if HAVE_SSO_LOGIN:

var HAVE_SSO_LOGIN = true;
var SSO_TOKEN_EXPIRE_DT = new Date('${SSO_TOKEN_EXPIRE_DT}'); // in UTC
var SSO_CHAR_ID = '${SSO_CHAR_ID}';
var SSO_CHAR_NAME = '${SSO_CHAR_NAME|js_escape}';
var SSO_CORP_ID = '${SSO_CORP_ID}';
var SSO_CORP_NAME = '${SSO_CORP_NAME|js_escape}';
var SSO_SHIP_ID = '${SSO_SHIP_ID}';
var SSO_SHIP_NAME = '${SSO_SHIP_NAME|js_escape}';
var SSO_SHIP_TITLE = '${SSO_SHIP_TITLE|js_escape}';
var SSO_SOLARSYSTEM_ID = '${SSO_SOLARSYSTEM_ID}';
var SSO_SOLARSYSTEM_NAME = '${SSO_SOLARSYSTEM_NAME|js_escape}';
var SSO_IS_DOCKED = false;
var SSO_IS_ONLINE = false;
window.setTimeout(evesso_refresher, 2000);

% else:

var HAVE_SSO_LOGIN = false;
var SSO_IS_ONLINE = false;
var SSO_TOKEN_EXPIRE_DT = new Date(new Date().getTime()); // current time in UTC

%endif