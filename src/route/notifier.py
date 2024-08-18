#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-16 20:39:12

from typing import List, Dict, Callable
from flask import Blueprint
from flask import request, jsonify, redirect, url_for
from datetime import timedelta
from model.conf import logger, conf
from route.base import baseconf
from model.fetcher import get_fetcher
from model import notifier as notifier
from model.notifier import BaseNotifier
from model.job import get_runfunc
import copy
import easycron

notifier_blueprint = Blueprint('notifier', __name__, url_prefix='/notifier')
__idx2notifierfunc: Dict[int, Callable] = {}


def register(notifier: BaseNotifier, notifier_idx: int) -> None:
    fetcher = get_fetcher(baseconf)
    func = get_runfunc(fetcher, notifier)
    minutes = notifier.interval_minutes
    easycron.register(func, interval=timedelta(minutes=minutes))
    __idx2notifierfunc[notifier_idx] = func


def cancel(notifier_idx: int) -> None:
    func = __idx2notifierfunc.pop(notifier_idx)
    easycron.cancel(func)


def get_notifiers(conf: dict, default_interval: int) -> List[BaseNotifier]:
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
            logger.info(f'notifier config "{notifier_name}" not valid, skip...')
            continue
        notifier_: BaseNotifier = notifier_class(**kwargs)
        notifier_idx = len(notifiers)
        register(notifier_, notifier_idx)
        notifiers.append(notifier_)
    return notifiers


default_interval = baseconf['default_interval_minutes']
notifiers: List[BaseNotifier] = get_notifiers(conf, default_interval)


@notifier_blueprint.route('/add', methods=['POST'])
def add_notifier():
    notifier_cls = request.form.get('cls')
    notifier_name = request.form.get('name')
    notifier_name = notifier_cls if not notifier_name else notifier_name
    try:
        notifier_class: BaseNotifier = getattr(notifier, notifier_cls)
    except Exception:
        logger.info(f'notifier class "{notifier_cls}" not found, skip...')

    interval = request.form.get('interval_minutes', default_interval)
    kwargs = copy.deepcopy({k: v for k, v in request.form.items()})
    kwargs.pop('cls')
    kwargs['interval_minutes'] = default_interval if not interval else interval
    if not notifier_class.config_params_is_valid(kwargs):
        logger.info(f'notifier config of "{notifier_name}" not valid, skip...')
    notifier_: BaseNotifier = notifier_class(**kwargs)
    notifier_idx = len(notifiers)
    register(notifier_, notifier_idx)
    notifiers.append(notifier_)
    return redirect(url_for('index', _anchor='added_notifier'))
    # return jsonify({'status': 'success', 'message': 'Notifier added'})


@notifier_blueprint.route('/del', methods=['GET'])
def delete_notifier():
    notifier_idx = request.args.get('idx', type=int)
    notifiers.pop(notifier_idx)
    cancel(notifier_idx)
    return redirect(url_for('index', _anchor='deleted_notifier'))
    # return jsonify({'status': 'success', 'message': 'Notifier deleted'})


@notifier_blueprint.route('/edit', methods=['POST'])
def edit_notifier():
    notifier_idx: int = request.form.get('idx', type=int)
    kwargs = {k: v for k, v in request.form.items() if v}
    kwargs.pop('idx')
    notifier_ = notifiers[notifier_idx]
    old_interval_minutes = notifier_.interval_minutes
    notifier_.update(**kwargs)
    new_interval_minutes = notifier_.interval_minutes
    if old_interval_minutes != new_interval_minutes:
        notifiers.pop(notifier_idx)
        cancel(notifier_idx)
        notifier_idx = len(notifiers)
        register(notifier_, notifier_idx)
        notifiers.append(notifier_)
    return redirect(url_for('index', _anchor='edited_notifier'))
    # return jsonify({'status': 'success', 'message': 'Notifier updated'})


@notifier_blueprint.route('/', methods=['GET'])
def get_notifiers():
    return jsonify({'notifiers': notifiers})
