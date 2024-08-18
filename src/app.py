#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wyn
# Time: 2024-08-16 20:34:14

from flask import Flask, render_template, redirect, url_for
from route.notifier import notifier_blueprint, notifiers
from route.base import base_blueprint, baseconf
from model.notifier import get_notifier_class
from model.conf import save_conf
import copy
import easycron

app = Flask(__name__)
app.register_blueprint(base_blueprint)
app.register_blueprint(notifier_blueprint)


@app.route('/')
def index():
    notifier_classes = get_notifier_class()
    return render_template('index.html',
                           baseconf=baseconf,
                           notifiers=notifiers,
                           notifier_classes=notifier_classes)


@app.route('/save', methods=['GET'])
def save_notifier():
    conf = copy.deepcopy(baseconf)
    conf['notifiers'] = [notifier_.dump_conf() for notifier_ in notifiers]
    save_conf(conf)
    return redirect(url_for('index', _anchor='saved'))


if __name__ == '__main__':
    easycron.run(block=False)
    app.run(host='0.0.0.0', port=4100)
