#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

db = sqlite3.connect('data.db', check_same_thread=False)


def add(id, creator_id):
    sql = "INSERT INTO channels VALUES ('%s', '%s')" % (id, creator_id)
    db.execute(sql)
    db.commit()


def delete(id):
    sql = "DELETE FROM channels WHERE id='%s'" % (id)
    db.execute(sql)
    db.commit()


def get(id = None, creator_id = None, limit = None, count = False):
    sql_array = []
    sql_array.append('SELECT')
    if count:
        sql_array.append('COUNT(*)')
    else:
        sql_array.append('*')
    sql_array.append('FROM channels')
    if id or creator_id:
        sql_array.append('WHERE')
        if id:
            sql_array.append("id='%s'" % (id))
        if id and creator_id:
            sql_array.append('AND')
        if creator_id:
            sql_array.append("creator_id='%s'" % (creator_id))
    if limit:
        sql_array.append('LIMIT %d' % (limit))

    sql = ' '.join(sql_array)
    ret = db.execute(sql).fetchall()
    if count:
        return ret[0][0]
    else:
        return ret
