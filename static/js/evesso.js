/*
 External vars:
 HAVE_SSO_LOGIN: bool - if the user is authorized
 SSO_TOKEN_EXPIRE_DT: Date, in UTC - sso token expiraion date
 
 // notes:
 // new Date(new Date().getTime()); // current time in UTC
*/

function evesso_refresher() {
    console.log('evesso_refresher()');
    if (HAVE_SSO_LOGIN) window.setTimeout(evesso_refresher, 15000);
    return;
}
