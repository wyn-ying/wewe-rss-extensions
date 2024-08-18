#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-18 19:19:44

from typing import Callable
from datetime import datetime
from model.fetcher import DbFetcher
from model.notifier import BaseNotifier
from model.conf import logger


def get_runfunc(fetcher: DbFetcher, notifier: BaseNotifier) -> Callable:
    def wrapper_func():
        now_minute = datetime.now().replace(second=0, microsecond=0)
        if not notifier.is_active:
            return
        interval = notifier.interval_minutes
        cur_data = fetcher.get_recent_data(interval)
        logger.info(f'Notifier[{notifier.name}] active at {now_minute}, curr articles num: {len(cur_data)}')
        if len(cur_data) == 0:
            return
        message = notifier.generate_message(cur_data)
        notifier.send(message)
    return wrapper_func
