# -*- coding: utf-8 -*-
from time import sleep

import httpx
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

from common import engine_class
from spider import BaseTranslate
from spider.transl_sougou import SougouTranslate
from utils import baidu_ocr

__all__ = [
    'MouseCheckThread',
    'EngineThread',
    'TranslThread',
    'VoiceThread',
    'OCRThread',
]


class MouseCheckThread(QThread):
    """鼠标相对悬浮窗位置监测"""
    trigger = pyqtSignal(bool)

    def __init__(self, widget: QWidget):
        super(MouseCheckThread, self).__init__()
        self.widget = widget
        self.quit_flag = False

    def quit(self):
        self.quit_flag = True
        super().quit()

    def run(self):
        offset = 20  # 鼠标超出 widget 边缘的距离（单位：像素）
        widget_w = self.widget.width()  # widget 的宽度
        widget_h = self.widget.height()  # widget 的高度
        widget_pos = self.widget.pos()  # widget 左上角的坐标
        while True:
            # 退出线程时结束循环
            if self.quit_flag:
                break
            mouse_pos = QCursor.pos()  # 鼠标当前坐标
            pos = mouse_pos - widget_pos  # 鼠标相对 widget 左上角的坐标
            if not (-offset <= pos.x() <= widget_w + offset and -offset <= pos.y() <= widget_h + offset):
                # 鼠标超出 widget 边缘一定距离后，发送信号并结束循环
                self.trigger.emit(True)
                break
            sleep(0.1)


class EngineThread(QThread):
    """创建翻译引擎对象"""
    trigger = pyqtSignal(dict)

    def __init__(self, select: str):
        super(EngineThread, self).__init__()
        self.select = select

    def run(self):
        result = {'code': 0, 'msg': 'OK', 'obj': None}
        try:
            engine = engine_class.get(self.select)
            obj = engine()  # 实例化翻译引擎
        except (httpx.ConnectError, httpx.ProxyError, httpx.ConnectTimeout) as exc:
            result.update({'msg': str(exc)})
        else:
            result.update({'code': 1, 'obj': obj})
        self.trigger.emit(result)  # 发送信号


class TranslThread(QThread):
    """启动翻译"""
    trigger = pyqtSignal(dict)

    def __init__(self, engine: BaseTranslate, **kwargs):
        super(TranslThread, self).__init__()
        self.engine = engine
        self.kwargs = kwargs

    def run(self):
        result = {'code': 1, 'msg': 'OK'}
        if self.engine.__class__.__name__ == 'YoudaoTranslate':
            self.kwargs.pop('from_lan', None)
        try:
            self.engine.translate(**self.kwargs)
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout) as exc:
            # 翻译失败
            result.update({'code': 0, 'msg': str(exc)})
            self.trigger.emit(result)
        else:
            # 翻译完成
            self.trigger.emit(result)


class VoiceThread(QThread):
    """下载发音"""
    trigger = pyqtSignal(bytes)

    def __init__(self, engine: BaseTranslate, *args):
        super(VoiceThread, self).__init__()
        self.engine = engine
        self.args = args

    def run(self):
        try:
            data = self.engine.get_tts(*self.args)
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout):
            data = bytes()
        self.trigger.emit(data)  # 发送数据


class OCRThread(QThread):
    """文字识别"""
    trigger = pyqtSignal(str)

    def __init__(self, image: bytes, from_lan):
        super().__init__()
        self.image = image
        self.from_lan = from_lan

    def run(self):
        try:
            # text = baidu_ocr(self.image)  # 百度API，精度较高
            # text = BaiduTranslate().get_ocr(self.image)  # 百度翻译接口，精度较低
            text = SougouTranslate().get_ocr(self.image)  # 搜狗翻译接口，精度适中
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout):
            text = ''
        self.trigger.emit(text)  # 信号发送文本
