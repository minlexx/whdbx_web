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
 SSO_IS_DOCKED: bool, true if caharacter is docked in structure
 SSO_IS_ONLINE: bool, true if caharacter is in game
*/


// variables used in this script:
var evesso_errors_count = 0;
var evesso_max_errors = 20;
// Limit ship refreshing time to once a minute, despite it is cached only for 5 seconds on API side;
//        we are not that interested in ship anyway.
var evesso_last_ship_refresh_time = 0; // timestamp in milliseconds
var evesso_ship_refresh_interval = 60*1000; // in milliseconds
// Limit online refreshing time to once a minute, because it is cached for 60 seconds
var evesso_last_online_refresh_time = 0; // timestamp in milliseconds
var evesso_online_refresh_interval = 60*1000; // in milliseconds


function evesso_is_expired() {
    var dt_now = new Date(new Date().getTime()); // current time in UTC
    // console.log('evesso_is_expired: ' + dt_now.getTime() + ' >= ' + SSO_TOKEN_EXPIRE_DT.getTime() + '?');
    if (dt_now.getTime() >= SSO_TOKEN_EXPIRE_DT.getTime()) {
        return true;
    }
    return false;
}


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
            console.log('evesso_request_public_data:   char_id:   ' + data.char_id);
            console.log('evesso_request_public_data:   char_name: ' + data.char_name);
            console.log('evesso_request_public_data:   corp_id:   ' + data.corp_id);
            console.log('evesso_request_public_data:   corp_name: ' + data.corp_name);
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
            window.setTimeout(evesso_refresher, 3000);
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
            console.log('evesso_request_location_ship:   ship_name:      ' + data.ship_name);
            console.log('evesso_request_location_ship:   ship_type_id:   ' + data.ship_type_id);
            console.log('evesso_request_location_ship:   ship_type_name: ' + data.ship_type_name);
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
            window.setTimeout(evesso_refresher, 3000);
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


function evesso_request_location_online() {
    jQuery.ajax({
        'url': '/ajax',
        'data': {'esi_call': 'location_online'},
        'method': 'GET',
        'timeout': 15000,
        'dataType': 'json',
        'cache': false
    })
    .done(function(data, textStatus, jqXHR) {
        if (data.error == '') {
            evesso_errors_count = 0;  // clear errors counter
            evesso_last_online_refresh_time = new Date().getTime(); // remember time (in ms)
            console.log('evesso_request_location_online:  OK');
            console.log('evesso_request_location_online:   is_online: ' + data.is_online);
            // update
            SSO_IS_ONLINE = data.is_online;
            // update html
            if (SSO_IS_ONLINE) {
                $('#character_info_online_img').attr('src', '/static/img/online.png');
                $('#character_info_online_img').attr('onmouseover', 'Tip(\'Online\');');
            } else {
                $('#character_info_online_img').attr('src', '/static/img/offline.png');
                $('#character_info_online_img').attr('onmouseover', 'Tip(\'Offline\');');
            }
            // restart refresher
            window.setTimeout(evesso_refresher, 3000);
        } else {
            console.log('evesso_request_location_online: JSON request was OK, but returned error :(');
            console.log('evesso_request_location_online:      data.error: ' + data.error);
            if (evesso_check_errors_and_logout()) return;
            // still can retry
            window.setTimeout(evesso_refresher, 10000);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('evesso_request_location_online: failed: [' + textStatus + ']');
        console.log('evesso_request_location_online: failed: will retry in 10 seconds');
        // if this fails too many times, probably we are not logged in anymore
        if (evesso_check_errors_and_logout()) return;
        // still can retry
        window.setTimeout(evesso_refresher, 10000);
    });
}


function evesso_request_location() {
    // switch image status to "Loading..."
    $('#character_info_ss_img').attr('src', '/static/img/location_64.gif');
    //
    jQuery.ajax({
        'url': '/ajax',
        'data': {'esi_call': 'location'},
        'method': 'GET',
        'timeout': 15000,
        'dataType': 'json',
        'cache': false
    })
    .done(function(data, textStatus, jqXHR) {
        if (data.error == '') {
            evesso_errors_count = 0;  // clear errors counter
            console.log('evesso_request_location:  OK');
            console.log('evesso_request_location:   solarsystem_id:   ' + data.solarsystem_id);
            console.log('evesso_request_location:   solarsystem_name: ' + data.solarsystem_name);
            console.log('evesso_request_location:   is_docked:        ' + data.is_docked);
            console.log('evesso_request_location:   is_whsystem:      ' + data.is_whsystem);
            console.log('evesso_request_location:   structure_id:     ' + data.structure_id);
            console.log('evesso_request_location:   station_id:       ' + data.station_id);
            // update
            SSO_SOLARSYSTEM_ID = data.solarsystem_id;
            SSO_SOLARSYSTEM_NAME = data.solarsystem_name;
            SSO_IS_DOCKED = data.is_docked;
            var SOLARSYSTEM_NAME_ESC = SSO_SOLARSYSTEM_NAME.replace(/'/g, "\\'"); // escape single quotes
            // update html: change soo image to Loaded
            $('#character_info_ss_img').attr('src', '/static/img/solarsystem_icon_64.png');
            // update html
            var docked_str = SSO_IS_DOCKED ? '<br />(docked)' : '';
            if (data.is_whsystem) {
                // show link to system
                $("#character_info_location_name_block").html(''
                  + '<a href="/' + SSO_SOLARSYSTEM_NAME + '" '
                  + ' title="Show info: ' + SOLARSYSTEM_NAME_ESC + '" '
                  + ' onmouseover="Tip(\'' + SOLARSYSTEM_NAME_ESC + '\');" '
                  + ' onmouseout="UnTip();">' + SSO_SOLARSYSTEM_NAME + '</a>'
                  + docked_str);
            } else {
                // do not show link to system
                $("#character_info_location_name_block").html(''
                  + '<b>' + SSO_SOLARSYSTEM_NAME + '</b>'
                  + docked_str);
            }
            // restart refresher
            window.setTimeout(evesso_refresher, 15000);
        } else {
            console.log('evesso_request_location: JSON request was OK, but returned error :(');
            console.log('evesso_request_location:      data.error: ' + data.error);
            // do not change HTML content in case of request error
            //$("#character_info_location_name_block").html('Error');
            if (evesso_check_errors_and_logout()) return;
            // still can retry
            window.setTimeout(evesso_refresher, 15000);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('evesso_request_location: failed: [' + textStatus + ']');
        console.log('evesso_request_location: failed: will retry in 15 seconds');
        $("#character_info_location_name_block").html('Error');
        // if this fails too many times, probably we are not logged in anymore
        if (evesso_check_errors_and_logout()) return;
        // still can retry
        window.setTimeout(evesso_refresher, 15000);
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
    
    // check if character public data is known; if not, request it
    if ((SSO_CHAR_ID == '') || (SSO_CORP_ID == '')) {
        console.log('evesso_refresher:  trigger the request of public data.');
        evesso_request_public_data();
        return;
    }
    
    // update character's online status
    var ms_since_last_refresh = new Date().getTime() - evesso_last_online_refresh_time;
    if (ms_since_last_refresh > evesso_online_refresh_interval)
    {
        console.log('evesso_refresher:  trigger the request of character online status.');
        evesso_request_location_online();
        return;
    }

    // update character's ship
    ms_since_last_refresh = new Date().getTime() - evesso_last_ship_refresh_time;
    if ((SSO_SHIP_ID == '') || (SSO_SHIP_NAME == '') ||
        (ms_since_last_refresh > evesso_ship_refresh_interval))
    {
        console.log('evesso_refresher:  trigger the request of character ship.');
        evesso_request_location_ship();
        return;
    }
    
    evesso_request_location();
    
    // evesso_request_location() will set us timeouts.
    // if (HAVE_SSO_LOGIN) window.setTimeout(evesso_refresher, 15000);
    return;
}


function evesso_request_open_window_information(target_id) {
    // do not send request to open window in client, if the character is offline
    if (!SSO_IS_ONLINE) return;
    // simple ajax request, no data is received, only OK/fail status
    jQuery.ajax({
        'url': '/ajax',
        'data': {'esi_call': 'ui_open_window_information', 'target_id': target_id},
        'method': 'GET',
        'timeout': 15000,
        'dataType': 'json',
        'cache': false
    })
    .done(function(data, textStatus, jqXHR) {
        if (data.error == '') {
            console.log('evesso_request_open_window_information:  OK');
        } else {
            console.log('evesso_request_open_window_information: JSON request was OK, but returned error :(');
            console.log('evesso_request_open_window_information:      data.error: ' + data.error);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('evesso_request_open_window_information: failed: [' + textStatus + ']');
    });
}


function showTypeInfo(type_id) {
    console.log('showTypeInfo: type_id=' + type_id);
    // ESI call 'open window informtaion' is not implemented for type IDs :(
}


function showCharInfo(char_id) {
    console.log('showCharInfo: char_id=' + char_id);
    evesso_request_open_window_information(char_id);
}


function showCorpInfo(corp_id) {
    console.log('showCorpInfo: corp_id=' + corp_id);
    evesso_request_open_window_information(corp_id);
}


function showAllianceInfo(ally_id) {
    console.log('showAllianceInfo: ally_id=' + ally_id);
    evesso_request_open_window_information(ally_id);
}
