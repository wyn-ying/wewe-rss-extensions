#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-17 17:37:24

from flask import Blueprint
from flask import request, redirect, url_for
from model.conf import conf

base_blueprint = Blueprint('base', __name__, url_prefix='/base')


def get_base(conf) -> dict:
    baseconf = {}
    for key in ('default_interval_minutes', 'db_provider', 'db_url', 'wewerss_origin_url'):
        baseconf[key] = conf[key]
    return baseconf


baseconf = get_base(conf)


@base_blueprint.route('/edit', methods=['POST'])
def edit_notifier():
    default_min: int = request.form.get('default_interval_minutes', type=int)
    if default_min:
        baseconf['default_interval_minutes'] = default_min
    db_provider = request.form.get('db_provider', type=str)
    if db_provider:
        baseconf['db_provider'] = db_provider
    db_url = request.form.get('db_url', type=str)
    if db_url:
        baseconf['db_url'] = db_url
    return redirect(url_for('index', _anchor='edited_base'))
    # return jsonify({'status': 'success', 'message': 'Notifier updated'})
