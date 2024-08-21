#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-20 22:12:11

from typing import Dict
from model.conf import conf
import requests


def get_feedid2name() -> Dict:
    ori_url = conf['wewerss_origin_url']
    url = f'{ori_url}/feeds'
    resp = requests.get(url)
    data = resp.json()
    return {i['id']: i['name'] for i in data}
