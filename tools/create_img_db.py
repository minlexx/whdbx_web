#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import sqlite3


def numeric_comparator(s):
    # 10000_64.png
    m = re.match(r'(\d+)_(\d+)\.png', s)
    if m is not None:
        itemid = int(m.group(1))
        return itemid
    raise ValueError(s)


def get_file_content(filename: str) -> bytes:
    f = open('../img/Types/' + filename, 'rb')
    ret = f.read()
    f.close()
    return ret


def main():
    print('CWD: ', os.getcwd())
    print('Scanning ../img/Types')

    files = os.listdir('../img/Types')
    files.sort(key=numeric_comparator)

    print(len(files), 'files')
    print(files)

    sq = sqlite3.connect('item_images.db')
    cur = sq.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS png(itemid INT, size INT, png BLOB, PRIMARY KEY(itemid, size))')
    sq.commit()
    cur.execute('CREATE INDEX IF NOT EXISTS png_itemid_index ON png (itemid, size)')
    sq.commit()

    num_inserted = 1
    num_total = len(files)
    for filename in files:
        m = re.match(r'(\d+)_(\d+)\.png', filename)
        if m is None:
            raise ValueError(filename)
        itemid = int(m.group(1))
        sz = int(m.group(2))
        print('Inserting {0}/{1} {2} ({3}, {4})'.format(
            num_inserted, num_total, filename, itemid, sz
        ))
        cur.execute('INSERT INTO png VALUES(?,?,?)', (itemid, sz, get_file_content(filename)))
        num_inserted += 1

    sq.commit()
    cur.close()
    sq.close()
    print('Done')

if __name__ == '__main__':
    main()
