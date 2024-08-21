#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-16 20:34:14

from flask import Flask, render_template, redirect, url_for, send_from_directory
from route.notifier import notifier_blueprint, notifiers
from route.base import base_blueprint, baseconf
from route.cron import cron_blueprint, feedcron
from model.notifier import get_notifier_class
from model.cron import get_feedid2name
from model.conf import save_conf, ENABLE_NOTIFIER, ENABLE_CRON
import copy
import easycron

app = Flask(__name__)
app.register_blueprint(base_blueprint)
if ENABLE_NOTIFIER:
    app.register_blueprint(notifier_blueprint)
if ENABLE_CRON:
    app.register_blueprint(cron_blueprint)


@app.route('/')
def index():
    context = {
        'baseconf': baseconf,
        'notifier_disable_info': ' [[Disable]]',
        'notifiers': [],
        'notifier_classes': [],
        'cron_disable_info': ' [[Disable]]',
        'feedid2name': {},
        'feedcron': {}
    }
    if ENABLE_NOTIFIER:
        context['notifier_disable_info'] = ''
        context['notifiers'] = notifiers
        context['notifier_classes'] = get_notifier_class()
    if ENABLE_CRON:
        context['cron_disable_info'] = ''
        context['feedid2name'] = get_feedid2name()
        context['feedcron'] = feedcron
    return render_template('index.html', **context)


@app.route('/favicon.ico')
def favicon():
    imgpath = 'ico.png'
    return send_from_directory(app.static_folder, imgpath, mimetype='image/png')


@app.route('/save', methods=['GET'])
def save_notifier():
    conf = copy.deepcopy(baseconf)
    if not ENABLE_NOTIFIER:
        for key in ('default_interval_minutes', 'db_provider', 'db_url'):
            conf.pop(key)
    else:
        conf['notifiers'] = [notifier_.dump_conf() for notifier_ in notifiers]
    if not ENABLE_CRON:
        for key in ('wewerss_origin_url',):
            conf.pop(key)
    else:
        conf['crons'] = feedcron
    save_conf(conf)
    return redirect(url_for('index', _anchor='saved'))


if __name__ == '__main__':
    easycron.run(block=False)
    app.run(host='0.0.0.0', port=4100)
