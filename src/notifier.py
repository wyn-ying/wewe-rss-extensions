#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wyn
# Time: 2024-07-28 17:40:29

from abc import ABC, abstractmethod
from datetime import datetime
from zoneinfo import ZoneInfo
from dingtalkchatbot.chatbot import DingtalkChatbot
import requests
import json
import logging
import sys

fmt = '%(asctime)s %(levelname)s %(filename)s %(funcName)s[%(lineno)d] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=fmt)
logger = logging.getLogger(__name__)


class BaseNotifier(ABC):

    cls_args = {'name', 'interval_minutes'}

    def __init__(self,
                 name: str = 'notifier',
                 interval_minutes: int = 240) -> None:
        self.name = name
        self.interval_minutes = interval_minutes
        self.tminfo = self._get_tminfo(interval_minutes)
        self.is_active = True

    def _get_tminfo(self, minutes: int) -> str:
        if minutes == int(minutes / 1440) * 1440:
            days = int(minutes / 1440)
            tminfo = f'{days}天'
        elif minutes == int(minutes / 60) * 60:
            hours = int(minutes / 60)
            tminfo = f'{hours}小时'
        else:
            tminfo = f'{minutes}分钟'
        return tminfo

    @classmethod
    @abstractmethod
    def config_params_is_valid(cls, conf: dict) -> bool:
        raise NotImplementedError(f'{cls.__name__}.config_params_is_valid() should be impl')

    def generate_title(self, minutes: int | None = None) -> str:
        tminfo = self.tminfo if minutes is None else self._get_tminfo(minutes)
        title = f'最近{tminfo} WeWe RSS 有以下新内容'
        return title

    @abstractmethod
    def generate_message(self, data: list) -> dict:
        raise NotImplementedError(f'{self.name}.generate_message() should be impl')

    def send(self, message: dict) -> None:
        try:
            self._send(message)
        except Exception as e:
            logger.info(f'[{self.name}] error during send(): {e}')
            logger.info(f'[{self.name}] skip curr notifier.send()...')

    @abstractmethod
    def _send(self, message: dict) -> None:
        raise NotImplementedError(f'{self.name}._send() should be impl')


class FeishuNotifier(BaseNotifier):
    def __init__(self,
                 fs_token: str,
                 name: str = 'feishu_notifier',
                 interval_minutes: int = 240) -> None:
        self.url = f'https://open.feishu.cn/open-apis/bot/v2/hook/{fs_token}'
        self.err_cnt = 0
        super().__init__(name, interval_minutes)
        title = 'WeWe RSS Notifier 连接测试'
        content = f'Wewe Rss Notifier **[{self.name}]** 配置成功'
        message = self._gen_markdown_message(title, content)
        self.send(message)

    @classmethod
    def config_params_is_valid(cls, conf: dict) -> bool:
        if 'fs_token' not in conf.keys():
            return False
        necessary_keys = {'fs_token', } | cls.cls_args
        if len(set(conf.keys()) - necessary_keys) > 0:
            return False
        return True

    def generate_message(self, datalist: list) -> dict:
        text = []
        create_time = None
        for item in datalist:
            name = item['mp_name']
            id_ = item['id']
            url = f'https://mp.weixin.qq.com/s/{id_}'
            title = item['title']
            c_time = datetime.fromtimestamp(item['created_at'])
            c_time = c_time.astimezone(ZoneInfo('Asia/Shanghai'))
            create_time = c_time if create_time is None else max(create_time, c_time)
            publish_time = datetime.fromtimestamp(item['publish_time'])
            publish_time = publish_time.astimezone(ZoneInfo('Asia/Shanghai'))
            text_content = f'- **{name}** [{title}]({url}) {publish_time:%Y-%m-%d %H:%M}'
            text.append(text_content)
        title = self.generate_title()
        markdown_text = f'WeWe RSS 更新时间 {create_time:%Y-%m-%d %H:%M}\n\n'
        markdown_text += '\n'.join(text)
        message = self._gen_markdown_message(title, markdown_text)
        return message

    def _gen_markdown_message(self, title: str, content: str) -> dict:
        message = {
            'msg_type': 'interactive',
            'card': {
                'elements': [{
                        'tag': 'div',
                        'text': {
                            'content': content,
                            'tag': 'lark_md'
                        }
                    }
                ],
                'header': {
                    'title': {
                        'content': title,
                        'tag': 'plain_text'
                    }
                }
            }
        }
        return message

    def _send(self, message: dict) -> None:
        response = requests.post(self.url, data=json.dumps(message))
        res = response.json()
        logger.info(f'Notifier[{self.name}] send res: {res}')
        if res.get('code', 0) != 0:
            self.err_cnt += 1
            if self.err_cnt > 3:
                logger.warning(f'Notifier[{self.name}] cant send over 3 times, auto inactivated')
                self.is_active = False


class DingtalkNotifier(BaseNotifier):
    def __init__(self,
                 access_token: str,
                 secret: str,
                 name: str = 'dingtalk_notifier',
                 interval_minutes: int = 240) -> None:
        self.url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}'
        self.xiaoding = DingtalkChatbot(self.url, secret=secret, pc_slide=True,
                                        fail_notice=False)
        self.err_cnt = 0
        super().__init__(name, interval_minutes)
        message = {
            'title': 'WeWe RSS Notifier 连接测试',
            'text': f'Wewe Rss Notifier **[{self.name}]** 配置成功',
        }
        self.send(message)

    @classmethod
    def config_params_is_valid(cls, conf: dict) -> bool:
        if 'access_token' not in conf.keys():
            return False
        if 'secret' not in conf.keys():
            return False
        necessary_keys = {'access_token', 'secret'} | cls.cls_args
        if len(set(conf.keys()) - necessary_keys) > 0:
            return False
        return True

    def generate_title(self, minutes: int | None = None) -> str:
        tminfo = self.tminfo if minutes is None else self._get_tminfo(minutes)
        title = f'## 最近{tminfo} WeWe RSS 有以下新内容 \n\n'
        return title

    def generate_message(self, datalist: list) -> dict:
        text = []
        create_time = None
        for item in datalist:
            name = item['mp_name']
            id_ = item['id']
            url = f'https://mp.weixin.qq.com/s/{id_}'
            title = item['title']
            c_time = datetime.fromtimestamp(item['created_at'])
            c_time = c_time.astimezone(ZoneInfo('Asia/Shanghai'))
            create_time = c_time if create_time is None else max(create_time, c_time)
            publish_time = datetime.fromtimestamp(item['publish_time'])
            publish_time = publish_time.astimezone(ZoneInfo('Asia/Shanghai'))
            text_content = f'> **{name}** [{title}]({url}) {c_time} {publish_time:%Y-%m-%d %H:%M}'
            text.append(text_content)
        title = self.generate_title()
        markdown_text = title + f'\n\nWeWe RSS 更新时间 {create_time:%Y-%m-%d %H:%M}\n\n'
        markdown_text += '\n\n'.join(text)
        message = {
            'title': title,
            'text': markdown_text
        }
        return message

    def _send(self, message: dict) -> None:
        title = message['title']
        text = message['text']
        res = self.xiaoding.send_markdown(title=title, text=text)
        logger.info(f'Notifier[{self.name}] send res: {res}')
        if res.get('errcode', 0) != 0:
            self.err_cnt += 1
            if self.err_cnt > 3:
                logger.warning(f'Notifier[{self.name}] cant send over 3 times, auto inactivated')
                self.is_active = False
