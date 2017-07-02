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

var evesso_renew_token_errors_count = 0;
var evesso_renew_token_max_errors = 10;

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
        console.log('evesso_renew_token: ' + data.error);
        console.log('evesso_renew_token: ' + data.sso_expire_dt_utc);
        if (data.error == '') {
            console.log('evesso_renew_token: OK');
            evesso_renew_token_errors_count = 0;  // clear errors counter
            // update for new token expiration date
            SSO_TOKEN_EXPIRE_DT = new Date(data.sso_expire_dt_utc)
            window.setTimeout(evesso_refresher, 2000);
        } else {
            console.log('evesso_renew_token: JSON request was OK, but returned error :(');
            evesso_renew_token_errors_count++;
            if (evesso_renew_token_errors_count > evesso_renew_token_max_errors) {
                console.log('evesso_renew_token: too many errors, stop trying.')
                HAVE_SSO_LOGIN = false;
                window.location.reload();
            } else {
                // still can retry
                window.setTimeout(evesso_refresher, 10000);
            }
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('evesso_renew_token: failed: ' + textStatus);
        console.log('evesso_renew_token: failed: data.error: ' + data.error);
        console.log('evesso_renew_token: failed: will retry in 10 seconds');
        // if this fails too many times, probably we are not logged in anymore
        evesso_renew_token_errors_count++;
        if (evesso_renew_token_errors_count > evesso_renew_token_max_errors) {
            console.log('evesso_renew_token: too many errors, stop trying.')
            HAVE_SSO_LOGIN = false;
            window.location.reload();
        } else {
            // still can retry
            window.setTimeout(evesso_refresher, 10000);
        }
    });
}


function evesso_refresher() {
    console.log('evesso_refresher: start');
    if (evesso_is_expired()) {
        console.log('evesso_refresher: EVE-SSO token has expired; trigger refresh.');
        evesso_renew_token();
        return;
    }
    
    if (HAVE_SSO_LOGIN) window.setTimeout(evesso_refresher, 15000);
    return;
}
