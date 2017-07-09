/*
 External vars:
 HAVE_SSO_LOGIN: bool - if the user is authorized
 SSO_TOKEN_EXPIRE_DT: Date, in UTC - sso token expiraion date
*/

function evesso_is_expired() {
    var dt_now = new Date(new Date().getTime()); // current time in UTC
    console.log('evesso_is_expired: ' + dt_now.getTime() + ' >= ' + SSO_TOKEN_EXPIRE_DT.getTime() + '?');
    if (dt_now.getTime() >= SSO_TOKEN_EXPIRE_DT.getTime()) {
        return true;
    }
    return false;
}

var evesso_errors_count = 0;
var evesso_max_errors = 10;


function evesso_check_errors_and_logout() {
    evesso_errors_count++;
    if (evesso_errors_count > evesso_max_errors) {
        console.log('evesso_check_errors_and_logout: too many errors, stop trying.')
        HAVE_SSO_LOGIN = false;
        window.location.reload();
        return true;
    }
    return false;
}


function evesso_renew_token() {
    jQuery.ajax({
        'url': '/ajax',
        'data': 'sso_refresh_token',
        'method': 'GET',
        'timeout': 15000,
        'dataType': 'json',
        'cache': false
    })
    .done(function(data, textStatus, jqXHR) {
        if (data.error == '') {
            evesso_errors_count = 0;  // clear errors counter
            console.log('evesso_renew_token: OK: ' + data.sso_expire_dt_utc);
            // update for new token expiration date
            SSO_TOKEN_EXPIRE_DT = new Date(data.sso_expire_dt_utc)
            window.setTimeout(evesso_refresher, 2000);
        } else {
            console.log('evesso_renew_token: JSON request was OK, but returned error :(');
            console.log('evesso_renew_token:      data.error: ' + data.error);
            if (evesso_check_errors_and_logout()) return;
            // still can retry
            window.setTimeout(evesso_refresher, 10000);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('evesso_renew_token: failed: [' + textStatus + ']');
        console.log('evesso_renew_token: failed: will retry in 10 seconds');
        // if this fails too many times, probably we are not logged in anymore
        if (evesso_check_errors_and_logout()) return;
        // still can retry
        window.setTimeout(evesso_refresher, 10000);
    });
}


function evesso_request_public_data() {
    jQuery.ajax({
        'url': '/ajax',
        'data': {'esi_call': 'public_data'},
        'method': 'GET',
        'timeout': 15000,
        'dataType': 'json',
        'cache': false
    })
    .done(function(data, textStatus, jqXHR) {
        if (data.error == '') {
            evesso_errors_count = 0;  // clear errors counter
            console.log('evesso_request_public_data:  OK');
            console.log('evesso_request_public_data:  char_id: ' + data.char_id);
            console.log('evesso_request_public_data:  char_name: ' + data.char_name);
            console.log('evesso_request_public_data:  corp_id: ' + data.corp_id);
            console.log('evesso_request_public_data:  corp_name: ' + data.corp_name);
            // update
            SSO_CHAR_ID = data.char_id;
            SSO_CHAR_NAME = data.char_name;
            SSO_CORP_ID = data.corp_id;
            SSO_CORP_NAME = data.corp_name;
            // TODO: update html
            window.setTimeout(evesso_refresher, 2000);
        } else {
            console.log('evesso_request_public_data: JSON request was OK, but returned error :(');
            console.log('evesso_request_public_data:      data.error: ' + data.error);
            if (evesso_check_errors_and_logout()) return;
            // still can retry
            window.setTimeout(evesso_refresher, 10000);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('evesso_request_public_data: failed: [' + textStatus + ']');
        console.log('evesso_request_public_data: failed: will retry in 10 seconds');
        // if this fails too many times, probably we are not logged in anymore
        if (evesso_check_errors_and_logout()) return;
        // still can retry
        window.setTimeout(evesso_refresher, 10000);
    });
}


function evesso_refresher() {
    console.log('evesso_refresher: start');
    
    // check access token expiration
    if (evesso_is_expired()) {
        console.log('evesso_refresher:  EVE-SSO token has expired; trigger refresh.');
        evesso_renew_token();
        return;
    }
    
    // check if character public data is known
    if ((SSO_CHAR_ID == '') || (SSO_CORP_ID == '')) {
        console.log('evesso_refresher:  trigger the request of public data.');
        evesso_request_public_data();
        return;
    }
    console.log('evesso_refresher:  no need to request public data.');
    
    if (HAVE_SSO_LOGIN) window.setTimeout(evesso_refresher, 15000);
    return;
}
