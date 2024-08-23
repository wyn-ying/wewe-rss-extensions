#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-19 12:57:07

from typing import List, Dict, Callable
from flask import Blueprint
from flask import request, jsonify, redirect, url_for
from model.conf import logger, conf
from model.job import get_cron_func
import copy
from croniter import croniter
import easycron

cron_blueprint = Blueprint('cron', __name__, url_prefix='/cron')
__feedcronidx2func: Dict[str, Callable] = {}


def register(feedid: str, cron_expr: str, cron_idx: int) -> None:
    func = get_cron_func(feedid)
    key = f'{feedid}@{cron_idx}'
    easycron.register(func, cron_expr=cron_expr)
    __feedcronidx2func[key] = func


def cancel(feedid: str, cron_idx: int) -> None:
    key = f'{feedid}@{cron_idx}'
    func = __feedcronidx2func.pop(key)
    easycron.cancel(func)


def init_feedcron(conf: dict) -> Dict[str, List[str]]:
    feedcron_conf: dict = conf.get('crons', {})
    for feedid, crons in feedcron_conf.items():
        for cron_idx, cron_expr in enumerate(crons):
            if not croniter.is_valid(cron_expr):
                info = f'({feedid = }, {cron_expr = })'
                logger.info(f'crons config {info} invalid, skip...')
                continue
            register(feedid, cron_expr, cron_idx)
    return copy.deepcopy(feedcron_conf)


feedcron = init_feedcron(conf)


@cron_blueprint.route('/add', methods=['POST'])
def add_cron():
    feedid = request.form.get('fid')
    cron_expression = request.form.get('cron_expression')
    if not croniter.is_valid(cron_expression):
        err_data = {'status': 'failed', 'message': 'Cron expression invalid'}
        return jsonify(err_data)

    if feedid not in feedcron.keys():
        feedcron[feedid] = []
    cron_idx = len(feedcron[feedid])
    register(feedid, cron_expression, cron_idx)
    feedcron[feedid].append(cron_expression)
    return redirect(url_for('index', _anchor='added_cron'))
    # return jsonify({'status': 'success', 'message': 'Cron added'})


@cron_blueprint.route('/del', methods=['GET'])
def delete_cron():
    feedid = request.args.get('fid', type=str)
    cron_idx = request.args.get('idx', type=int)
    cron = feedcron[feedid]
    cron.pop(cron_idx)
    if len(cron) == 0:
        feedcron.pop(feedid)
    return redirect(url_for('index', _anchor='deleted_cron'))
    # return jsonify({'status': 'success', 'message': 'Cron deleted'})


@cron_blueprint.route('/', methods=['GET'])
def get_cron():
    return jsonify({'cron': feedcron})
