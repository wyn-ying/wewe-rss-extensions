#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wyn
# Time: 2024-07-29 18:36:40

from typing import List, Dict
from datetime import datetime
from notifier import BaseNotifier
import fetcher
import notifier
import copy
import os
import sys
import yaml
import time
import logging

fmt = '%(asctime)s %(levelname)s %(filename)s %(funcName)s[%(lineno)d] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=fmt)
logger = logging.getLogger(__name__)


def get_fetcher(conf: dict,
                env_provider: str = None,
                env_url: str = None) -> fetcher.DbFetcher | None:
    if 'db_provider' in conf.keys():
        provider = conf['db_provider']
        if provider not in ('mysql', 'sqlite'):
            logger.warning('EXIT NOTIFIER: config of "db_provider" should be in ("mysql", "sqlite")')
            return None
    else:
        provider = env_provider
    url = conf.get('db_url', env_url)
    db_fetcher = fetcher.DbFetcher(provider, url)
    return db_fetcher


def get_notifiers(conf: dict, env_interval: int) -> List[BaseNotifier]:
    default_interval = conf.get('default_interval_minutes', env_interval)

    notifiers_conf: list = conf.get('notifiers', [])
    notifiers: List[BaseNotifier] = []
    for notifier_conf in notifiers_conf:
        notifier_cls = notifier_conf['cls']
        notifier_name = notifier_conf.get('name', notifier_cls)
        try:
            notifier_class: BaseNotifier = getattr(notifier, notifier_cls)
        except Exception:
            logger.info(f'notifier class "{notifier_cls}" not found, skip...')
            continue

        interval = notifier_conf.get('interval_minutes', default_interval)
        kwargs = copy.deepcopy(notifier_conf)
        kwargs.pop('cls')
        kwargs['interval_minutes'] = interval
        if not notifier_class.config_params_is_valid(kwargs):
            logger.info(f'notifier config of "{notifier_name}" not valid, skip...')
            continue
        notifier_ = notifier_class(**kwargs)
        notifiers.append(notifier_)
    return notifiers


def run_notifier():
    enable_notifier = os.environ.get('ENABLE_NOTIFIER', None)
    if not enable_notifier:
        msg = 'EXIT NOTIFIER: notifier module not enable. set anything '
        msg += 'to environment variable "ENABLE_NOTIFIER" to enable notifier'
        logger.warning(msg)
        return

    default_path = '/app/data/conf/notify.yaml'
    conf_path = os.environ.get('NOTIFIER_CONF_PATH', default_path)
    if not os.path.exists(conf_path):
        msg = f'EXIT NOTIFIER: notifier conf file: "{conf_path}" not exist. '
        msg += 'set correct filepath to environment variable NOTIFIER_CONF_PATH'
        logger.warning(msg)
        return
    with open(conf_path, 'r') as f:
        conf: dict = yaml.safe_load(f)

    env_provider = os.environ.get('DATABASE_TYPE')
    env_url = os.environ.get('DATABASE_URL')

    db_fetcher = get_fetcher(conf, env_provider, env_url)
    if db_fetcher is None:
        return

    env_interval = int(os.environ.get('NOTIFY_INTERVAL_MINUTES', 4 * 60))
    notifiers = get_notifiers(conf, env_interval)

    interval_notifier_map: Dict[int, List[BaseNotifier]] = {}
    for notifier_ in notifiers:
        interval = notifier_.interval_minutes
        if interval not in interval_notifier_map.keys():
            interval_notifier_map[interval] = []
        interval_notifier_map[interval].append(notifier_)

    last_executed = None
    start = datetime.now()
    start_minute = start.replace(second=0, microsecond=0)
    while True:
        time.sleep(1)
        now = datetime.now()
        now_minute = now.replace(second=0, microsecond=0)
        if now_minute == last_executed:
            continue
        timegap_minutes = int((now_minute - start_minute).seconds / 60)
        for interval, cur_notifiers in interval_notifier_map.items():
            if timegap_minutes % interval != 0:
                continue
            for notifier_ in cur_notifiers:
                if not notifier_.is_active:
                    continue
                cur_data = db_fetcher.get_recent_data(interval)
                logger.info(f'Notifier[{notifier_.name}] active at {now_minute}, curr articles num: {len(cur_data)}')
                if len(cur_data) == 0:
                    continue
                message = notifier_.generate_message(cur_data)
                notifier_.send(message)
                logger.info(f'Notifier[{notifier_.name}] finish sending')
        last_executed = now_minute


if __name__ == '__main__':
    now = datetime.now()
    logger.info(f'start at {now}')
    run_notifier()
