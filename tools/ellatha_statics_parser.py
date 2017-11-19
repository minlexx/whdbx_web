#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Downloads info for all static holes for all shattered WHs from ellatha.com
"""

import datetime
import os
import requests
import sqlite3
import time


class Db:
    def __init__(self):
        self.db = sqlite3.connect('../db/eve.db', check_same_thread=True)
        # self.db.row_factory = sqlite3.Row

    def get_all_shattered_whs(self) -> list:
        ret = []
        cur = self.db.cursor()
        q = 'SELECT solarsystemid, system, class, statics ' \
            ' FROM wormholesystems_new WHERE class<0 OR class >=13'
        cur.execute(q)
        for row in cur.fetchall():
            ret.append({'ssid': int(row[0]),
                        'name': str(row[1]),
                        'class': int(row[2]),
                        'statics': str(row[3])})
        return ret


def statics_equal(ell_s: str, ours: str):
    # split, sort our statics
    sts = sorted(ours.split(','))
    ours_s = ','.join(sts)
    # compare
    if ours_s != ell_s:
        # print('    statics difer: ours:[{}], ellatha:[{}]   '.format(ours_s, ell_s), end='')
        return False
    return True


def parse_ellatha_statics(text: str) -> str:
    ret = ''
    ret_list = []
    # <td bgcolor="#FFFFFF" width="20%"><b>Static WHs:</b>&nbsp;</td>
    # <td bgcolor="#F5F5F5"><a href="wormholelistview.asp?key=Wormhole+N110">N110</a> <a href="wormholelistview.asp?key=Wormhole+J244">J244</a> </td>
    if text != '':
        stt = text.find('<b>Static WHs:</b>')
        if stt == -1:
            return ret
        stt += 15
        stt = text.find('<a href="wormholelistview.asp?', stt)
        ent = text.find('</td>', stt)
        text = text[stt:ent]
        lines = text.split(' ')
        num_parts = len(lines)
        if num_parts > 0:
            i = 1
            while i < num_parts:
                line = lines[i]
                # parse: line = "href="wormholelistview.asp?key=Wormhole+N110">N110</a>"
                stt = line.find('">')
                ent = line.find('</a>')
                if (stt > 0) and (ent > 0):
                    stt += 2
                    static_name = line[stt:ent]
                    ret_list.append(static_name)
                i += 2
    ret_list = sorted(ret_list)
    ret = ','.join(ret_list)
    return ret


def get_ellatha_statics(whsys_name: str) -> str:
    ret = ''
    try:
        whsys_number = whsys_name[1:]
        url = 'http://www.ellatha.com/eve/WormholeSystemview.asp'
        params = {'key': whsys_number}
        r = requests.get(url, params=params)
        text = r.text
        ret = parse_ellatha_statics(text)
    except requests.RequestException as ex:
        print('Network error: {}'.format(str(ex)), end='')
    return ret


def parser_test():
    text = '<td bgcolor="#FFFFFF" width="20%"><b>Static WHs:</b>&nbsp;</td>' \
           '<td bgcolor="#F5F5F5"><a href="wormholelistview.asp?key=Wormhole+N110">N110</a> ' \
           '<a href="wormholelistview.asp?key=Wormhole+J244">J244</a> </td>'
    e = parse_ellatha_statics(text)
    print(e)


def create_sql_update_stmt(ssid: int, statics: str, comment: str) -> str:
    return 'UPDATE wormholesystems_new SET statics=\'{}\' ' \
            ' WHERE solarsystemid={};  -- {}\n'.format(statics, ssid, comment)


def main():
    print('Running in dir: {}'.format(os.getcwd()))

    db = Db()
    swhs = db.get_all_shattered_whs()

    print('Getting statics from ellatha (total: {})'.format(len(swhs)))

    to_update = []

    count = 1
    num_added_new = 0
    num_conflicted = 0
    num_errors = 0
    for swh in swhs:
        print('  {}/{}: {}... '.format(count, len(swhs), swh['name']), end='')
        e_statics = get_ellatha_statics(swh['name'])
        if e_statics == '':
            num_errors += 1
            print('ERROR')
        else:
            print(' {} '.format(e_statics), end='')
            if not statics_equal(e_statics, swh['statics']):
                if swh['statics'] == '':
                    to_update.append(create_sql_update_stmt(swh['ssid'], e_statics, swh['name']))
                    num_added_new += 1
                    print(' ADDED')
                else:
                    num_conflicted += 1
                    to_update.append(create_sql_update_stmt(swh['ssid'], e_statics, '{}; was: {}'.
                                                            format(swh['name'], swh['statics'])))
                    print(' UPDATED, was {}'.format(swh['statics']))
            else:
                print(' ALREADY_SAME')
        count += 1
        # test limiter
        # if count >= 2:
        #     break
        time.sleep(10)

    with open('../db/sqlite_sql/ellatha_statics.sql', mode='wt', encoding='utf-8') as f:
        cur_dt = datetime.datetime.utcnow()
        f.write('-- Shattered WHs statics data, gathered from ellatha.com at {} UTC\n'.format(str(cur_dt)))
        f.writelines(to_update)

    print('Processed {} shattered WHs'.format(len(swhs)))
    print('Errors: {}'.format(num_errors))
    print('New statics added: {}'.format(num_added_new))
    print('Conflicts count: {}'.format(num_conflicted))


if __name__ == '__main__':
    main()
    # parser_test()
