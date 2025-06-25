#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-18 19:21:04

from typing import Union
from urllib.parse import urlparse
from model.conf import logger
import mysql.connector
import sqlite3


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
        elif provider == 'zlz':
            parsed_url = urlparse(self.url)
            self.db = parsed_url.path[1:]
            self.conn_args = {
                'host': parsed_url.hostname,
                'port': parsed_url.port,
                'user': parsed_url.username,
                'password': parsed_url.password,
                'database': self.db
            }
            # 参考 rss_loader.py 的查询逻辑，查询 cnvp_mp_articles 表
            self.query_template = """
                SELECT a.original_id, a.title, a.links as pic_url,
                    UNIX_TIMESTAMP(CONVERT_TZ(a.publish_time, '+08:00', '+00:00')),
                    UNIX_TIMESTAMP(CONVERT_TZ(a.publish_time, '+08:00', '+00:00')),
                    b.mp_name
                FROM cnvp_mp_articles AS a, cnvp_feeds as b
                WHERE a.wxs_id = b.wxs_id
                AND a.publish_time - INTERVAL 480 MINUTE >= NOW() - INTERVAL {timebias} MINUTE
                ORDER BY a.publish_time DESC
                """
            self.db_timezone_bias = 0
        else:
            raise ValueError('provider should be in ("mysql", "sqlite", "zlz")')
        self.inited = False

    def check_initialized(self) -> bool:
        if self.provider == 'mysql':
            handler = mysql.connector.connect(**self.conn_args)
        elif self.provider == 'sqlite':
            handler = sqlite3.connect(self.url)
        elif self.provider == 'zlz':
            handler = mysql.connector.connect(**self.conn_args)

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
        elif self.provider == 'zlz':
            check_table_query = """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = %s;
            """
            cursor.execute(check_table_query, (self.db, 'cnvp_mp_articles'))
            table_exists = cursor.fetchone()[0] > 0
            if not table_exists:
                return False

        handler.close()
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
        elif self.provider == 'zlz':
            handler = mysql.connector.connect(**self.conn_args)
            
        cursor = handler.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        if self.provider == 'zlz':
            # 对于 zlz provider，需要生成ID并适配数据结构
            data = [
                {
                    "id": r[0],
                    "title": r[1],
                    "pic_url": r[2],
                    "created_at": int(r[3]),
                    "publish_time": int(r[4]),
                    "mp_name": r[5]
                } for i, r in enumerate(results)]
        else:
            data = [
                {
                    "id": r[0],
                    "title": r[1],
                    "pic_url": r[2],
                    "created_at": int(r[3]),
                    "publish_time": r[4],
                    "mp_name": r[5]
                } for r in results]
        
        handler.close()
        return data


def get_fetcher(conf: dict) -> Union[DbFetcher, None]:
    provider = conf['db_provider']
    if provider not in ('mysql', 'sqlite', 'zlz'):
        logger.warning('EXIT NOTIFIER: config of "db_provider" should be in ("mysql", "sqlite", "zlz")')
        return None
    url = conf['db_url']
    db_fetcher = DbFetcher(provider, url)
    return db_fetcher
