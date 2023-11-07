# -*- coding: utf-8 -*-
import base64
import sys

from PyQt5 import QtCore, QtWidgets, QtGui

from threads import MouseCheckThread
from utils import move_widget


class FramelessWidget(QtWidgets.QWidget):
    """ 自定义Widget(主窗口)
    1. 无边框、置顶/取消置顶
    2. 添加阴影
    3. 鼠标拖动
    """
    sizeChanged = QtCore.pyqtSignal(QtCore.QSize)

    def __init__(self, *args, **kwargs):
        super(FramelessWidget, self).__init__(*args, **kwargs)
        # 背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 无边框
        self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowMinMaxButtonsHint)
        # 初始化变量
        self.moveFlag = False
        self.initPos = None
        self.lastSize = None
        self.shadowWidth = 11  # 阴影宽度 = 内边距 + 2
        # 设置阴影效果
        self.setShadowEffect()

    def setShadowEffect(self):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self.shadowWidth)
        shadow.setColor(QtCore.Qt.gray)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        # 检测窗口变化
        if self.lastSize is not None and self.lastSize.width() != self.width():
            self.resize(self.lastSize)
        else:
            self.lastSize = self.size()
        # 绘制窗口背景
        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.setBrush(QtGui.QColor(240, 240, 240, 255))
        painter.setPen(QtCore.Qt.transparent)
        rect = self.rect()
        rect.setLeft(self.shadowWidth)
        rect.setTop(self.shadowWidth)
        rect.setWidth(rect.width() - self.shadowWidth)
        rect.setHeight(rect.height() - self.shadowWidth)
        painter.drawRoundedRect(rect, 0, 0)

    def mousePressEvent(self, event):
        """ 按下鼠标按键
        获取鼠标相对窗口的位置
        开启窗口跟随鼠标移动
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.initPos = event.globalPos() - self.pos()  # 鼠标相对窗口的位置
            self.moveFlag = True
            event.accept()

    def mouseMoveEvent(self, event):
        """ 鼠标移动
        窗口跟随鼠标移动
        """
        if QtCore.Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.initPos)  # 窗口跟随鼠标移动
            event.accept()

    def mouseReleaseEvent(self, event):
        """ 抬起鼠标按键
        关闭窗口跟随鼠标移动
        """
        self.moveFlag = False

    def closeEvent(self, event):
        """关闭主窗口同时关闭所有子窗口"""
        event.accept()
        sys.exit(0)


class FloatWidget(QtWidgets.QWidget):
    """ 自定义Widget(悬浮窗)
    1. 无边框、圆角、置顶
    2. 添加阴影
    3. 淡入/淡出
    4. 自动关闭
    """

    def __init__(self, *args, **kwargs):
        super(FloatWidget, self).__init__(*args, **kwargs)
        # 无边框置顶
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        # 背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 阴影效果
        self.effect = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect.setOffset(0, 0)
        self.effect.setBlurRadius(10)
        self.effect.setColor(QtGui.QColor(200, 200, 200))
        self.setGraphicsEffect(self.effect)
        # 淡入/淡出动画
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.setDuration(200)  # 动画持续时间

    def paintEvent(self, event):
        # 窗口背景
        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtCore.Qt.transparent)
        rect = self.rect()
        rect.setLeft(10)
        rect.setTop(10)
        rect.setWidth(rect.width() - 10)
        rect.setHeight(rect.height() - 10)
        painter.drawRoundedRect(rect, 10, 10)

    def showFullScreen(self):
        self.show()

    def show(self):
        """ 显示窗口
        移动窗口到鼠标的位置
        先显示窗口，再执行淡入动画
        扫描鼠标位置
        """
        # 先显示窗口再执行动画
        move_widget(self, QtGui.QGuiApplication.primaryScreen().geometry(), QtGui.QCursor.pos(), 10)  # 移动窗口到鼠标的位置
        super(FloatWidget, self).show()
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        # 自动关闭窗口
        self.check()

    def deleteLater(self):
        """ 回收窗口
        先执行淡出动画，再回收窗口
        """
        self.mouse_check_thread.disconnect()
        self.mouse_check_thread.quit()
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()
        self.animation.finished.connect(super(FloatWidget, self).deleteLater)

    def check(self):
        """ 检测鼠标位置
        通过线程扫描鼠标位置，当鼠标超出一定范围后自动关闭悬浮窗
        """
        self.mouse_check_thread = MouseCheckThread(self)
        self.mouse_check_thread.trigger.connect(self.deleteLater)
        self.mouse_check_thread.start()


class TextEdit(QtWidgets.QTextEdit):
    """ 自定义TextEdit
    1. 自定义右键菜单
    2. 插入文件时清空文本框
    3. 设置、取消阴影
    """
    def __init__(self, *args):
        super(TextEdit, self).__init__(*args)
        # 阴影设置
        self.effect = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect.setOffset(0, 2)
        self.effect.setBlurRadius(10)
        # 变量初始化
        self.clipboard = QtWidgets.QApplication.clipboard()

    # def contextMenuEvent(self, event):
    #     """自定义右键菜单"""
    #     menu = QtWidgets.QMenu()
    #     undo = menu.addAction("撤销")
    #     undo.setShortcut(QtGui.QKeySequence.Undo)
    #     redo = menu.addAction("恢复")
    #     redo.setShortcut(QtGui.QKeySequence.Redo)
    #     menu.addSeparator()
    #     cut = menu.addAction("剪切")
    #     cut.setShortcut(QtGui.QKeySequence.Cut)
    #     copy = menu.addAction("复制")
    #     copy.setShortcut(QtGui.QKeySequence.Copy)
    #     paste = menu.addAction("粘贴")
    #     paste.setShortcut(QtGui.QKeySequence.Paste)
    #     delete = menu.addAction("删除")
    #     menu.addSeparator()
    #     select_all = menu.addAction("选择全部")
    #     select_all.setShortcut(QtGui.QKeySequence.SelectAll)
    #
    #     if self.textCursor().selectedText():
    #         cut.setEnabled(True)
    #         copy.setEnabled(True)
    #         delete.setEnabled(True)
    #     else:
    #         cut.setDisabled(True)
    #         copy.setDisabled(True)
    #         delete.setDisabled(True)
    #     if self.clipboard.mimeData().formats():
    #         paste.setEnabled(True)
    #     else:
    #         paste.setDisabled(True)
    #     if self.toPlainText():
    #         select_all.setEnabled(True)
    #     else:
    #         select_all.setDisabled(True)
    #
    #     if self.isReadOnly():
    #         menu.removeAction(undo)
    #         menu.removeAction(redo)
    #         menu.removeAction(cut)
    #         menu.removeAction(paste)
    #         menu.removeAction(delete)
    #
    #     menu.move(event.pos())
    #     menu.show()
    #
    #     action = menu.exec_(self.mapToGlobal(event.pos()))
    #     if action == undo:
    #         self.undo()
    #     elif action == redo:
    #         self.redo()
    #     elif action == cut:
    #         self.cut()
    #     elif action == copy:
    #         self.copy()
    #     elif action == paste:
    #         self.paste()
    #     elif action == delete:
    #         self.textCursor().deleteChar()
    #     elif action == select_all:
    #         self.selectAll()

    def insertFromMimeData(self, mime_data: QtCore.QMimeData):
        """ 向文本框中插入数据
        1. 将剪切板的图片数据编码后转成QUrl，以实现向文本框粘贴图片
        2. 插入文件时先清空文本框，以便获取文件信息
        """
        image_data = mime_data.imageData()
        if image_data:
            # 图片数据来至剪切板，不能直接粘贴到文本框
            # 这里将图片数据编码后转成QUrl，以实现向文本框粘贴剪切板的图片
            buffer = QtCore.QBuffer(self)
            buffer.open(QtCore.QIODevice.WriteOnly)
            image_data.save(buffer, 'PNG')
            image_b64 = base64.b64encode(buffer.data()).decode()
            mime_data = QtCore.QMimeData()
            mime_data.setUrls([QtCore.QUrl('base64:///' + image_b64)])
        if mime_data.urls():
            # 向文本框中插入文件时先清空文本框，以便获取文件信息
            url_str = mime_data.urls()[0].url()
            if url_str.find('file:///') == 0 or url_str.find('base64:///') == 0:
                self.blockSignals(True)
                self.clear()
                self.blockSignals(False)
        super(TextEdit, self).insertFromMimeData(mime_data)

    def resizeEvent(self, event):
        """大小变化时调整阴影效果"""
        super(TextEdit, self).resizeEvent(event)
        if self.height() == self.minimumHeight():
            # 去除阴影
            self.effect.setColor(QtCore.Qt.transparent)
            self.setGraphicsEffect(self.effect)
        else:
            # 添加阴影
            self.effect.setColor(QtGui.QColor(240, 240, 240))
            self.setGraphicsEffect(self.effect)


class Label(QtWidgets.QLabel):
    """ 自定义Label
    鼠标移入隐藏，移出显示
    """
    def __init__(self, *args):
        super(Label, self).__init__(*args)

    def enterEvent(self, event):
        """鼠标移入隐藏"""
        self.hide()

    def leaveEvent(self, event):
        """鼠标移出显示"""
        self.show()


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    """ 自定义项目委托
    使 QListView 或 QTableView 等控件支持富文本渲染
    """
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)

        # 通过QTextDocument设置HTML代码
        doc = QtGui.QTextDocument()
        doc.setHtml(option.text)
        option.text = ''  # 清空源文本

        style = option.widget.style() if option.widget.style() else QtWidgets.QApplication.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)
        rect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, option)

        painter.save()
        painter.translate(rect.topLeft())  # 坐标变换，将左上角设置为原点
        painter.setClipRect(rect.translated(-rect.topLeft()))  # 设置HTML绘制区域

        context = QtGui.QAbstractTextDocumentLayout.PaintContext()
        doc.documentLayout().draw(painter, context)
        painter.restore()
