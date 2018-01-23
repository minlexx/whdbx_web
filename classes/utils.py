# -*- coding: utf-8 -*-
import re
from classes import tr_support


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
    if n_s == '0':
        return '0'
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


def is_whsystem_name(name: str) -> bool:
    if name.lower() == 'thera': return True  # special case
    if len(name) != 7: return False  # must be 7 chars
    if name[0] not in ['j', 'J']: return False  # 1st letter should be j or J
    name = name[1:]  # other 6 characters must be numbers
    m = re.match(r'^[0123456789]+$', name)
    if m is None: return False
    return True


def js_escape(s: str) -> str:
    return s.replace("'", "\\'")


def length_limit_20(s: str) -> str:
    s = s[:20]
    return s
