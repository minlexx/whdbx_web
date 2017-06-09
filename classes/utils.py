# -*- coding: utf-8 -*-


def dump_object(o):
    ret = ''
    if o is None:
        return None
    if type(o) == dict:
        for k in o:
            ret += str(k) + ': ' + str(o[k])
            ret += '\n'
        return ret
    if type(o) == list:
        ret = '['
        for o1 in o:
            ret += dump_object(o1)
            ret += ', '
        ret += ']'
        return ret
    for att in o.__dict__:
        ret += str(att) + ': ' + str(o.__dict__[att])
        ret += '\n'
    return ret


def dotted_number(n_s: str) -> str:
    ret = ''
    n = int(n_s)
    nc = n
    is_negative = False
    if n < 0:
        nc = n * (-1)
        is_negative = True
    while nc > 0:
        if ret != '':
            ret = '.' + ret
        rest = nc % 1000
        nc //= 1000
        if nc > 0:
            ret = str(rest).zfill(3) + ret
        else:
            ret = str(rest) + ret
    if is_negative:
        ret = '-' + ret
    return ret
