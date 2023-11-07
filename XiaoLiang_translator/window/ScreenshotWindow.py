# -*- coding: utf-8 -*-
from PyQt5.QtCore import QRect, qAbs, Qt, pyqtSignal, QBuffer, QIODevice
from PyQt5.QtGui import QCursor, QColor, QKeySequence, QPen, QPainter, QGuiApplication
from PyQt5.QtWidgets import QWidget, QShortcut, QApplication

from utils import move_widget
from widgets import Label


class ScreenshotWindow(QWidget):
    """截图窗口"""
    completed = pyqtSignal(bytes)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化窗口
        self.setMouseTracking(True)  # 鼠标追踪
        self.setCursor(Qt.CrossCursor)  # 十字光标
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 无边框置顶
        # 初始化变量
        self.screenGeometry = QGuiApplication.primaryScreen().geometry()
        self.pixelRatio = int(QApplication.primaryScreen().devicePixelRatio())
        self.fullScreenImage = QGuiApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
        self.pressLeftButton = False
        self.beginPos = None
        self.endPos = None
        self.captureImage = None
        self.painter = QPainter()
        self.pen = QPen(QColor(30, 144, 245), 1, Qt.SolidLine, Qt.RoundCap)
        # 创建提示框
        self.createTipBox()
        # Esc 键取消截屏
        QShortcut(QKeySequence(self.tr("Esc")), self, self.cancel)

    def createTipBox(self):
        """创建提示框"""
        self.label = Label(self)
        self.label.setText("按住鼠标左键选择翻译区域<br>按下鼠标右键或Esc键取消截屏")
        self.label.setStyleSheet("QLabel {background-color: rgba(0, 0, 0, 150); "
                                 "font: 14px \"微软雅黑\"; "
                                 "color: rgb(255, 255, 255); "
                                 "padding: 5px}")
        self.label.setObjectName("label")

    def mousePressEvent(self, event):
        """ 鼠标按键按下
        左键按下记录鼠标按下位置
        """
        if event.button() == Qt.LeftButton:
            # 关闭提示框
            self.label.close()
            # 点击鼠标左键开始截图
            self.beginPos = event.pos()
            self.pressLeftButton = True

    def mouseReleaseEvent(self, event):
        """ 鼠标按键抬起
        记录鼠标抬起位置
        退出截图，并发送结束信号和截图
        """
        if event.button() == Qt.LeftButton:
            self.endPos = event.pos()
            self.finish()  # 截屏完毕
        elif event.button() == Qt.RightButton:
            self.cancel()  # 取消截屏

    def mouseMoveEvent(self, event):
        """ 鼠标移动
        更新鼠标移动位置
        提示框跟随鼠标移动
        """
        if self.pressLeftButton:
            self.endPos = event.pos()
            self.update()
        else:
            move_widget(self.label, self.screenGeometry, event.pos())  # 提示框跟随鼠标移动

    def paintEvent(self, event):
        """绘制屏幕选区"""
        self.painter.begin(self)  # 开始重绘
        self.painter.drawPixmap(0, 0, self.fullScreenImage)
        self.painter.fillRect(self.fullScreenImage.rect(), QColor(0, 0, 0, 60))  # 黑色半透明遮罩
        self.painter.setPen(self.pen)  # 蓝色画笔
        if self.pressLeftButton and self.beginPos is not None and self.endPos is not None:
            pickRect = self.getRectangle(self.beginPos, self.endPos)  # 获得要截图的矩形框
            self.captureImage = self.fullScreenImage.copy(QRect(
                pickRect.x() * self.pixelRatio,
                pickRect.y() * self.pixelRatio,
                pickRect.width() * self.pixelRatio,
                pickRect.height() * self.pixelRatio
            ))  # 获取矩形框内的图片
            self.painter.drawPixmap(pickRect.topLeft(), self.captureImage)  # 填充截取的图片
            self.painter.drawRect(pickRect)  # 画矩形边框
        self.painter.end()  # 结束重绘

    def getRectangle(self, beginPoint, endPoint):
        """获取屏幕选区"""
        pickRectWidth = int(qAbs(beginPoint.x() - endPoint.x())) + 1
        pickRectHeight = int(qAbs(beginPoint.y() - endPoint.y())) + 1
        pickRectTop = beginPoint.x() if beginPoint.x() < endPoint.x() else endPoint.x()
        pickRectLeft = beginPoint.y() if beginPoint.y() < endPoint.y() else endPoint.y()
        pickRect = QRect(pickRectTop, pickRectLeft, pickRectWidth, pickRectHeight)
        return pickRect

    def show(self):
        self.showFullScreen()

    def showFullScreen(self):
        """ 启动截屏
        获取屏幕，显示截屏窗口
        """
        self.label.show()  # 显示提示框
        move_widget(self.label, self.screenGeometry, QCursor.pos())  # 刷新提示框位置
        super(ScreenshotWindow, self).showFullScreen()  # 全屏显示截图窗口

    def finish(self):
        """ 截屏完毕
        通过信号发送截取的图片
        截图完成自动退出截图
        """
        # 截图数据转 QBuffer
        buffer = QBuffer(self)
        buffer.open(QIODevice.WriteOnly)
        if self.captureImage:
            self.captureImage.save(buffer, 'PNG')
        self.completed.emit(bytes(buffer.data()))  # 发送信号
        self.deleteLater()  # 回收窗口

    def cancel(self):
        """ 取消截屏
        清空截图数据，发送完成信号
        """
        self.captureImage = None
        self.finish()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = ScreenshotWindow()
    window.show()
    sys.exit(app.exec_())
