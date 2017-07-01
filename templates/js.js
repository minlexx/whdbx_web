## -*- coding: utf-8 -*-

% if HAVE_SSO_LOGIN:
var HAVE_SSO_LOGIN = true;
var SSO_TOKEN_EXPIRE_DT = new Date('${SSO_TOKEN_EXPIRE_DT}'); // in UTC
window.setTimeout(evesso_refresher, 2000);
% else:
var HAVE_SSO_LOGIN = false;
var SSO_TOKEN_EXPIRE_DT = new Date(new Date().getTime()); // current time in UTC
%endif
