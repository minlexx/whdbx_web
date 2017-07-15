/*
 External vars:
 HAVE_SSO_LOGIN: bool - if the user is authorized
 SSO_TOKEN_EXPIRE_DT: Date, in UTC - eve-sso token expiraion date
 SSO_CHAR_ID: string, character id
 SSO_CHAR_NAME: string, character name
 SSO_CORP_ID: string, corporation id
 SSO_CORP_NAME: string, corporation name
 SSO_SHIP_ID: string, ship type id
 SSO_SHIP_NAME: string, ship type name
 SSO_SHIP_TITLE: string, ship name given by user
 SSO_SOLARSYSTEM_ID: string, current solar system id
 SSO_SOLARSYSTEM_NAME: string, current solar system name
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
            var CORP_NAME_ESC = SSO_CORP_NAME.replace(/'/g, "\\'"); // escape single quotes
            // update html
            $("#character_info_corp_block").html(''
              + '<a href="#" onclick="showCorpInfo(' + SSO_CORP_ID + '); return false;" '
              + ' title="Show info: ' + CORP_NAME_ESC + '" '
              + ' onmouseover="Tip(\'' + CORP_NAME_ESC + '\');" '
              + ' onmouseout="UnTip();">'
              + '<img src="https://imageserver.eveonline.com/Corporation/' + SSO_CORP_ID + '_32.png" />'
              + '</a>');
            $("#character_info_corp_name_block").html(''
              + '<a href="#" onclick="showCorpInfo(' + SSO_CORP_ID + '); return false;" '
              + ' title="Show info: ' + CORP_NAME_ESC + '" '
              + ' onmouseover="Tip(\'' + CORP_NAME_ESC + '\');" '
              + ' onmouseout="UnTip();">' + SSO_CORP_NAME + '</a>');
            // restart refresher
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


var evesso_last_ship_refresh_time = 0; // timestamp in milliseconds
var evesso_ship_refresh_interval = 60*1000; // in milliseconds

function evesso_request_location_ship() {
    jQuery.ajax({
        'url': '/ajax',
        'data': {'esi_call': 'location_ship'},
        'method': 'GET',
        'timeout': 15000,
        'dataType': 'json',
        'cache': false
    })
    .done(function(data, textStatus, jqXHR) {
        if (data.error == '') {
            evesso_errors_count = 0;  // clear errors counter
            evesso_last_ship_refresh_time = new Date().getTime(); // remember time (in ms)
            console.log('evesso_request_location_ship:  OK');
            console.log('evesso_request_location_ship:  ship_name: ' + data.ship_name);
            console.log('evesso_request_location_ship:  ship_type_id: ' + data.ship_type_id);
            console.log('evesso_request_location_ship:  ship_type_name: ' + data.ship_type_name);
            // update
            SSO_SHIP_ID = data.ship_type_id;
            SSO_SHIP_NAME = data.ship_type_name;
            SSO_SHIP_TITLE = data.ship_name;
            var SHIP_NAME_ESC = SSO_SHIP_NAME.replace(/'/g, "\\'"); // escape single quotes
            var SHIP_TITLE_ESC = SSO_SHIP_TITLE.replace(/'/g, "\\'"); // escape single quotes
            // update html
            $("#character_info_ship_block").html(''
              + '<a href="#" onclick="showTypeInfo(' + SSO_SHIP_ID + '); return false;" '
              + ' title="Show info: ' + SHIP_NAME_ESC + '" '
              + ' onmouseover="Tip(\'' + SHIP_NAME_ESC + '\');" '
              + ' onmouseout="UnTip();">'
              + '<img src="https://imageserver.eveonline.com/Type/' + SSO_SHIP_ID + '_32.png" />'
              + '</a>');
            $("#character_info_ship_name_block").html(''
              + '<a href="#" onclick="showTypeInfo(' + SSO_SHIP_ID + '); return false;" '
              + ' title="Show info: ' + SHIP_NAME_ESC + '" '
              + ' onmouseover="Tip(\'' + SHIP_NAME_ESC + '\');" '
              + ' onmouseout="UnTip();">' + SSO_SHIP_TITLE + '</a>');
            // restart refresher
            window.setTimeout(evesso_refresher, 2000);
        } else {
            console.log('evesso_request_location_ship: JSON request was OK, but returned error :(');
            console.log('evesso_request_location_ship:      data.error: ' + data.error);
            if (evesso_check_errors_and_logout()) return;
            // still can retry
            window.setTimeout(evesso_refresher, 10000);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('evesso_request_location_ship: failed: [' + textStatus + ']');
        console.log('evesso_request_location_ship: failed: will retry in 10 seconds');
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

    // update character's ship
    var ms_since_last_refresh = new Date().getTime() - evesso_last_ship_refresh_time;
    console.log('evesso_refresher:  ms_since_last_refresh = ' + ms_since_last_refresh)
    if ((SSO_SHIP_ID == '') || (SSO_SHIP_NAME == '') ||
        (ms_since_last_refresh > evesso_ship_refresh_interval))
    {
        console.log('evesso_refresher:  trigger the request of character ship.');
        evesso_request_location_ship();
        return;
    }
    console.log('evesso_refresher:  no need to request character ship.');
    
    if (HAVE_SSO_LOGIN) window.setTimeout(evesso_refresher, 15000);
    return;
}
