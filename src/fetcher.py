#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wyn
# Time: 2024-07-28 14:36:32

import mysql.connector
from urllib.parse import urlparse
import sqlite3
import logging
import sys

fmt = '%(asctime)s %(levelname)s %(filename)s %(funcName)s[%(lineno)d] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=fmt)
logger = logging.getLogger(__name__)


class DbFetcher:
    def __init__(self, provider: str, url: str) -> None:
        self.provider = provider
        self.url = url
        if provider == 'mysql':
            parsed_url = urlparse(self.url)
            self.db = parsed_url.path[1:]
            self.conn_args = {
                'host': parsed_url.hostname,
                'port': parsed_url.port,
                'user': parsed_url.username,
                'password': parsed_url.password,
                'database': self.db
            }
            self.query_template = """
                SELECT a.id, a.title, a.pic_url, UNIX_TIMESTAMP(a.created_at), a.publish_time, b.mp_name
                FROM articles AS a, feeds AS b
                WHERE a.mp_id = b.id
                AND a.created_at >= NOW() - INTERVAL {timebias} MINUTE
                ORDER BY a.publish_time DESC;
                """
            # fix time bias from UTC to local timezone
            self.db_timezone_bias = 8 * 60
        elif provider == 'sqlite':
            if self.url.startswith('file:..'):
                self.url = self.url.replace('file:..', '/app')
            self.query_template = """
                SELECT a.id, a.title, a.pic_url, a.created_at / 1000, a.publish_time, b.mp_name
                FROM articles AS a, feeds AS b
                WHERE a.mp_id = b.id
                AND a.created_at >= strftime('%s', 'now', '-{timebias} minutes') * 1000
                ORDER BY a.publish_time DESC;
                """
            self.db_timezone_bias = 0
        else:
            raise ValueError('provider should be in ("mysql", "sqlite")')
        self.inited = False

    def check_initialized(self) -> bool:
        if self.provider == 'mysql':
            handler = mysql.connector.connect(**self.conn_args)
        elif self.provider == 'sqlite':
            handler = sqlite3.connect(self.url)

        cursor = handler.cursor()
        if self.provider == 'mysql':
            check_table_query = """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = %s;
            """
            for table in ('articles', 'feeds'):
                cursor.execute(check_table_query, (self.db, table))
                table_exists = cursor.fetchone()[0] > 0
                if not table_exists:
                    return False
        elif self.provider == 'sqlite':
            check_table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
            for table in ('articles', 'feeds'):
                cursor.execute(check_table_query, (table,))
                table_exists = cursor.fetchone() is not None
                if not table_exists:
                    return False

        return True

    def get_recent_data(self, minutes: int = 240) -> list:
        if not self.inited:
            self.inited = self.check_initialized()
            if not self.inited:
                return []
        fixed_bias_minutes = minutes + self.db_timezone_bias
        query = self.query_template.format(timebias=fixed_bias_minutes)

        if self.provider == 'mysql':
            handler = mysql.connector.connect(**self.conn_args)
        elif self.provider == 'sqlite':
            handler = sqlite3.connect(self.url)
        cursor = handler.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        data = [
            {
                "id": r[0],
                "title": r[1],
                "pic_url": r[2],
                "created_at": int(r[3]),
                "publish_time": r[4],
                "mp_name": r[5]
            } for r in results]
        return data
