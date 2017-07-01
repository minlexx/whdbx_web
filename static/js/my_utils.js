
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
