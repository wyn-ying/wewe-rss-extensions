#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-16 21:21:32

import os
import sys
import copy
import yaml
import logging

fmt = '%(asctime)s %(levelname)s %(filename)s %(funcName)s[%(lineno)d] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=fmt)
logger = logging.getLogger(__name__)

default_path = './conf/conf.yaml'
conf_path = os.environ.get('CONF_PATH', default_path)
if not os.path.exists(conf_path):
    if not os.path.exists(os.path.dirname(conf_path)):
        os.makedirs(os.path.dirname(conf_path), exist_ok=True)
    with open(conf_path, 'w') as file:
        file.write('')
    msg = f'CONF FILE: "{conf_path}" not exist. auto created'
    logger.warning(msg)

ENABLE_NOTIFIER = True if os.environ.get('ENABLE_NOTIFIER') else False
ENABLE_CRON = True if os.environ.get('ENABLE_CRON') else False

with open(conf_path, 'r') as f:
    conf: dict = yaml.safe_load(f)
    if conf is None:
        conf = {}
    if ENABLE_NOTIFIER:
        if 'default_interval_minutes' not in conf.keys():
            env_interval = int(os.environ.get('NOTIFY_INTERVAL_MINUTES', 4 * 60))
            conf['default_interval_minutes'] = env_interval

        if 'db_provider' not in conf.keys():
            env_provider = os.environ.get('DATABASE_TYPE')
            conf['db_provider'] = env_provider
        provider = conf['db_provider']
        if provider not in ('mysql', 'sqlite'):
            logger.warning('EXIT NOTIFIER: config of "db_provider" should be in ("mysql", "sqlite")')
            sys.exit(1)

        if 'db_url' not in conf.keys():
            env_url = os.environ.get('DATABASE_URL')
            conf['db_url'] = env_url
        db_url = conf['db_url']
        if db_url is None:
            logger.warning('EXIT NOTIFIER: config of "db_url" should be set')
            sys.exit(1)
    else:
        conf['default_interval_minutes'] = 0
        conf['db_provider'] = 'disable'
        conf['db_url'] = 'disable'

    if ENABLE_CRON:
        if 'wewerss_origin_url' not in conf.keys():
            env_url = os.environ.get('WEWERSS_ORIGIN_URL')
            conf['wewerss_origin_url'] = env_url
        origin_url = conf['wewerss_origin_url']
        if origin_url is None and ENABLE_CRON:
            logger.warning('EXIT CRON: config of "wewerss_origin_url" should be set')
            sys.exit(1)
    else:
        conf['wewerss_origin_url'] = 'disable'


def save_conf(new_conf: dict) -> None:
    ori_conf = copy.deepcopy(conf)
    ori_conf.update(new_conf)
    with open(conf_path, 'w') as f:
        yaml.dump(ori_conf, f)
