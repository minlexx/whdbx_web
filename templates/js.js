## -*- coding: utf-8 -*-

% if HAVE_SSO_LOGIN:
var HAVE_SSO_LOGIN = true;
var SSO_TOKEN_EXPIRE_DT = new Date('${SSO_TOKEN_EXPIRE_DT}'); // in UTC
var SSO_CHAR_ID = '${SSO_CHAR_ID}';
var SSO_CHAR_NAME = '${SSO_CHAR_NAME}';
var SSO_CORP_ID = '${SSO_CORP_ID}';
var SSO_CORP_NAME = '${SSO_CORP_NAME}';
var SSO_SHIP_ID = '${SSO_SHIP_ID}';
var SSO_SHIP_NAME = '${SSO_SHIP_NAME}';
var SSO_SOLARSYSTEM_ID = '${SSO_SOLARSYSTEM_ID}';
var SSO_SOLARSYSTEM_NAME = '${SSO_SOLARSYSTEM_NAME}';
window.setTimeout(evesso_refresher, 2000);
% else:
var HAVE_SSO_LOGIN = false;
var SSO_TOKEN_EXPIRE_DT = new Date(new Date().getTime()); // current time in UTC
%endif
