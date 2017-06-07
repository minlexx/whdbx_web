## -*- coding: utf-8 -*-


function showhide(id, display_type) {
    var element = document.getElementById(id);
    if( !element ) return false;
    if( element.style.display == 'none' ) {
        if (display_type != undefined)
            element.style.display = display_type;
        else
            element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
    return true;
}


function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}


var g_xmlhttp = null;

function myajax(url, handler) {
    if(g_xmlhttp == null) {
        g_xmlhttp = new XMLHttpRequest();
    }
    g_xmlhttp.onreadystatechange = handler;
    g_xmlhttp.open("GET", url, true);
    g_xmlhttp.send();
}


function hole_search_handler() {
    if( g_xmlhttp == null ) return false;
    var res_div = document.getElementById('fast_search_result');
    if( !res_div ) return false;
    var resp = '';
    if( g_xmlhttp.readyState==4 && g_xmlhttp.status==200 ) {
        resp = g_xmlhttp.responseText;
    }
    if( (resp != '') && (resp != 'ERROR') ) {
        res_div.innerHTML = '[' + resp + ']';
        var obj = JSON.parse(resp);
        // { "maxJumpMass": 300000000, "maxStableMass": 3000000000,
        //   "in_class_str": "C5", "in_class": 5, "massRegeneration": 0,
        //   "maxStableTime": 1440, "name": "H900", "id": 46 }
        // tip string
        var tip_str = '';
        // mass
        tip_str += 'Масса: <b>';
        tip_str += obj.maxStableMass / 1000000;
        tip_str += '</b>  тыс.тонн<br />';
        // jump mass
        tip_str += 'Масса на прыг: <b>';
        tip_str += obj.maxJumpMass / 1000000;
        tip_str += '</b>  тыс.тонн<br />';
        // lifetime
        tip_str += 'Время жизни: <b>';
        tip_str += obj.maxStableTime / 60;
        tip_str += '</b>  ч.<br />';
        // element code
        var s = '<span class=\"static_name\" onmouseover=\"Tip(\'';
        s += tip_str;
        s += '\');\" onmouseout=\"UnTip();\">';
        s += obj.name;
        s += ' ' + obj.in_class_str;
        s += '</span>'
        res_div.innerHTML = s;
    }
    return true;
}


function jsystem_search_handler() {
    if( g_xmlhttp == null ) return false;
    var res_div = document.getElementById('fast_search_result');
    if( !res_div ) return false;
    var resp = '';
    if( g_xmlhttp.readyState==4 && g_xmlhttp.status==200 ) {
        resp = g_xmlhttp.responseText;
    }
    if( (resp != '') && (resp != 'ERROR') ) {
        res_div.innerHTML = 'id=[' + resp + ']';
        window.location = '/' + resp;
    }
    if (resp == 'ERROR') {
        res_div.innerHTML = 'Ошибка!';
    }
    return true;
}


function fast_search_hole() {
    var inp = document.getElementById('hole');
    var res_div = document.getElementById('fast_search_result');
    if( !inp || !res_div )
        return false;
    var s_h = inp.value;
    if( s_h.length == 4 ) {
        var msg = 'Поиск дыры: ' + s_h;
        res_div.innerHTML = msg;
        var url = '/ajax/?search_hole=' + encodeURIComponent(s_h)
        myajax(url, hole_search_handler)
    }
    return true;
}


function fast_search_system() {
    var inp = document.getElementById('ssys');
    var res_div = document.getElementById('fast_search_result');
    if( !inp || !res_div ) {
        return false;
    }
    var ss = inp.value;
    var do_search = false;
    if((ss.length == 7) && ((ss[0] == 'J') || (ss[0]=='j'))) {
        do_search = true; // Jxxxxxx / jxxxxxx
        ss = ss.toUpperCase();
    }
    if((ss.length == 6) && (isNumber(ss))) {
        do_search = true; // xxxxxx / xxxxxx, where xxxxxx are numbers
        ss = 'J' + ss;
    }
    if( ss.toLowerCase() == 'thera' )
        do_search = true; // Thera !
    if( do_search ) {
        var msg = 'Поиск: ' + ss;
        res_div.innerHTML = msg;
        var url = '/ajax/?search_jsystem=' + encodeURIComponent(ss)
        myajax(url, jsystem_search_handler)
    }
    return true;
}


function reportstatic_search_handler() {
    if( g_xmlhttp == null ) return false;
    var res_div = document.getElementById('new_statics_report_result');
    if( !res_div ) return false;
    var resp = '';
    if( g_xmlhttp.readyState==4 && g_xmlhttp.status==200 ) {
        resp = g_xmlhttp.responseText;
    }
    if (resp == 'OK') {
        res_div.innerHTML = resp;
        window.location.reload();
    } else {
        res_div.innerHTML = '<span class=\"sec_color_0\">'
            + resp + '</span>';
    }
}


function report_statics(ssid) {
    var inp = document.getElementById('new_statics');
    var res = document.getElementById('new_statics_report_result');
    if (!inp || !res) return false;
    var ss = inp.value;
    if (ss.length < 4) {
        res.innerHTML = '<span class=\"sec_color_0\">Неверный формат ввода!</span>';
        return;
    }
    res.innerHTML = 'Отправка запроса....';
    var url = '/ajax/?report_statics=' + encodeURIComponent(ss)
        + '&ssid=' + encodeURIComponent(ssid)
    console.log(url)
    myajax(url, reportstatic_search_handler)
}
