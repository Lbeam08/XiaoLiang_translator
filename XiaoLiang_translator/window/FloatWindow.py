# -*- coding: utf-8 -*-
import html
from time import sleep

from PyQt5.QtCore import QIODevice, QBuffer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QApplication

from ui.FloatWindow_ui import Ui_FloatWindow
from threads import VoiceThread
from utils import generate_output, b64decode_json
from widgets import FloatWidget


class FloatWindow(FloatWidget, Ui_FloatWindow):
    """悬浮窗口"""
    radioButtonClicked = pyqtSignal(bool)
    pushButtonClicked = pyqtSignal(str)
    textBrowserAnchorClicked = pyqtSignal(str)

    def __init__(self, query: str, *args, **kwargs):
        # 窗口初始化
        super().__init__(*args, **kwargs)
        # 窗口设置
        font = QFont('微软雅黑')
        font.setPixelSize(14)
        self.setFont(font)
        self.setupUi(self)
        # 翻译内容
        self.query = query
        # 信号连接
        self.radioButton.clicked.connect(lambda x: self.radioButtonClicked.emit(self.radioButton.isChecked()))
        self.pushButton.clicked.connect(lambda x: self.pushButtonClicked.emit(self.query))
        self.textBrowser_2.anchorClicked.connect(self.anchorClicked)
        # 初始化输出
        self.setQuery(self.query)
        # 剪切板
        self.clipboard = QApplication.clipboard()

    def setQuery(self, s):
        self.query = s
        self.textBrowser.setText("<b>{}</b>".format(html.escape(self.query)))
        self.textBrowser_2.setText("<i style='color: #606060;'>正在翻译...</i>")

    def output(self, obj):
        """输出翻译结果"""
        self.engine = obj
        translation_contents, explanation_contents = generate_output(obj)
        if not (translation_contents or explanation_contents):
            self.textBrowser_2.setText('<div style="color: #FF3C3C;">翻译结果为空，请重试</div>')
        else:
            self.textBrowser_2.setText(explanation_contents or translation_contents)

    def anchorClicked(self, url):
        """ 点击输出框中的链接
        点击输出框中音标发音按钮时，获取单词发音并播放
        """
        url = url.url().replace('#', '')
        res = b64decode_json(url)
        if isinstance(res, list):
            # 通过线程下载并播放发音
            self.tts(*res)
        else:
            # 发送点击的文本
            self.textBrowserAnchorClicked.emit(res)

    def tts(self, *args):
        """ 文本转语音
        下载 TTS 并播放
        """
        def trigger(data):
            """播放语音"""
            # 将语音写入缓冲区
            buffer = QBuffer(self)
            buffer.setData(data)
            buffer.open(QIODevice.ReadOnly)
            # 创建播放器
            player = QMediaPlayer(self)
            player.setVolume(100)
            player.setMedia(QMediaContent(), buffer)
            sleep(0.1)  # 延时等待 setMedia 完成。
            # 播放语音
            player.play()

        self.voice_thread = VoiceThread(self.engine, *args)
        self.voice_thread.trigger.connect(trigger)
        self.voice_thread.start()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = FloatWindow('测试')
    window.show()
    sys.exit(app.exec_())
