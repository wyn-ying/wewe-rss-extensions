#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-20 22:12:11

from typing import Dict
from model.conf import conf
import requests


def get_feedid2name() -> Dict:
    rss = conf.get('rss', 'wewe')
    if rss == 'wewe':
        ori_url = conf['wewerss_origin_url']
        url = f'{ori_url}/feeds'
        resp = requests.get(url)
        data = resp.json()
        return {i['id']: i['name'] for i in data}
    elif rss == 'zlz':
        from urllib.parse import urlparse
        import mysql.connector
        parsed_url = urlparse(conf['db_url'])
        conn_args = {
            'host': parsed_url.hostname,
            'port': parsed_url.port,
            'user': parsed_url.username,
            'password': parsed_url.password,
            'database': parsed_url.path[1:]
        }
        conn = mysql.connector.connect(**conn_args)
        cursor = conn.cursor()
        sql = 'SELECT wxs_id, mp_name FROM cnvp_feeds;'
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
        return {i[0]: i[1] for i in data}

