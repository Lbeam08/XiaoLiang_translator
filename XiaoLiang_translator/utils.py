# -*- coding: utf-8 -*-
import base64
import html
import json
import random
from typing import Literal

from Crypto.Cipher import AES
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QWidget
from aip import AipOcr

from spider import BaseTranslate

__all__ = [
    'aes_encrypt',
    'aes_decrypt',
    'move_widget',
    'baidu_ocr',
    'b64encode_json',
    'b64decode_json',
    'generate_output',
]


def aes_encrypt(
        text: str,
        key: str,
        iv: str = None,
        mode: Literal[1, 2, 3, 5, 6] = AES.MODE_CBC,
        padding: Literal['PKCS7', 'ZeroPadding', 'ISO10126', 'AnsiX923', 'NoPadding'] = 'PKCS7'
):
    """AES加密"""
    # 根据填充模式计算填充字符，并与原文进行拼接
    text = text.encode('utf-8')
    pad_num = AES.block_size - len(text) % AES.block_size
    if padding == 'PKCS7':
        pad_text = chr(pad_num) * pad_num
    elif padding == 'ZeroPadding':
        pad_text = chr(0) * pad_num
    elif padding == 'ISO10126':
        pad_text = ''.join([chr(random.randint(0, 9)) for _ in range(pad_num - 1)]) + chr(pad_num)
    elif padding == 'AnsiX923':
        pad_text = chr(0) * (pad_num - 1) + chr(pad_num)
    else:
        pad_text = ''
    pad_text = pad_text.encode('utf-8')
    text += pad_text
    # AES加密
    key = key.encode('utf-8')
    if mode in [AES.MODE_ECB, AES.MODE_CTR]:
        cipher = AES.new(key, mode)
    else:
        iv = iv.encode('utf-8')
        cipher = AES.new(key, mode, iv)
    encrypted_bytes = cipher.encrypt(text)
    # Base64编码
    base64_bytes = base64.b64encode(encrypted_bytes)
    base64_str = base64_bytes.decode('utf-8')
    return base64_str


def aes_decrypt(
        text: str,
        key: str,
        iv: str = None,
        mode: Literal[1, 2, 3, 5, 6] = AES.MODE_CBC,
        padding: Literal['PKCS7', 'ZeroPadding', 'ISO10126', 'AnsiX923', 'NoPadding'] = 'PKCS7'
):
    """AES解密"""
    # Base64解码
    base64_bytes = base64.b64decode(text)
    # AES解密
    key = key.encode('utf-8')
    if mode in [AES.MODE_ECB, AES.MODE_CTR]:
        cipher = AES.new(key, mode)
    else:
        iv = iv.encode('utf-8')
        cipher = AES.new(key, mode, iv)
    decrypted_bytes = cipher.decrypt(base64_bytes)
    decrypted_str = decrypted_bytes.decode('utf-8')
    # 去除填充字符
    pad_num = ord(decrypted_str[-1])
    if pad_num < AES.block_size:
        if padding == 'ZeroPadding':
            decrypted_str = decrypted_str.rstrip(chr(0))
        elif padding in ['PKCS7', 'ISO10126', 'AnsiX923']:
            decrypted_str = decrypted_str[:-pad_num]
    return decrypted_str


def move_widget(widget: QWidget, geometry: QRect, cursor: QPoint, offset: int = 20):
    """ 移动窗口到鼠标所在位置，并保持窗口始终显示在屏幕内

    :param widget: 窗口部件
    :param geometry: 屏幕信息
    :param cursor: 鼠标指针
    :param offset: 窗口与鼠标指针的间距
    """
    w = geometry.width()  # 屏幕宽
    h = geometry.height()  # 屏幕高
    x = cursor.x() + offset  # 鼠标X坐标
    y = cursor.y() + offset  # 鼠标Y坐标
    # 保持部件始终显示在屏幕内
    if x + widget.width() > w:  # 窗口右侧超出边界
        x = w - widget.width() if x - widget.width() < offset * 2 else x - widget.width() - offset * 2
    if y + widget.height() > h:  # 窗口底部超出边界
        y = h - widget.height() if y - widget.height() < offset * 2 else y - widget.height() - offset * 2
    widget.move(x, y)  # 移动窗口


def baidu_ocr(img_bytes):
    """ 利用百度文字识别API提取图片中的文本
    申请地址：https://console.bce.baidu.com/ai/?_=1630920729906#/ai/ocr/overview/index
    """
    APP_ID = ''
    API_KEY = ''
    SECRECT_KEY = ''
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
    # 通用文字识别（标准版），50000次/天免费
    message = client.basicGeneral(img_bytes, options={'detect_language': 'true'})
    # 通用文字识别（高精度版），500次/天免费
    # message = client.basicAccurate(img_bytes, options={'language_type': 'auto_detect'})
    try:
        text = ' '.join([words['words'] for words in message['words_result']])
    except (KeyError, TypeError):
        return ''
    return text


def b64encode_json(o):
    """base64编码（JSON）"""
    b64ec = base64.b64encode(json.dumps(o).encode())
    return b64ec.decode()


def b64decode_json(s):
    """base64解码（JSON）"""
    b64dc = base64.b64decode(s)
    return json.loads(b64dc.decode())


def generate_output(obj: BaseTranslate, more=False, reverse=False):
    """ 生成HTML输出内容

    :param obj: 翻译引擎对象
    :param more: 显示更多内容（默认不添加单词语法和双语例句）
    :param reverse: 有道词典--中日互译 结果切换
    :return: HTML字符串
    """
    # 输出内容1：译文
    translation_text, _ = obj.get_translation()
    translation_html = '<div style="font-size: 16px; color: #3C3C3C;">{}</div>'
    translation_contents = translation_html.format(html.escape(translation_text).replace('\n', '<br>'))

    # 输出内容2：释义
    explanations = obj.get_explanation(reverse)
    if not explanations:
        # 没有释义时直接返回译文
        return translation_contents, ''
    no_html = '<span style="color: #8C8C8C;">{}</span>'
    speech_html = '<a style="text-decoration: none;" href="#{}">🔊</a>'
    explanation_html = '<div style="font-size: 14px; color: #3C3C3C;">{}</div>'
    explanation_list = []
    for explanation in explanations:
        # 音标/读音
        symbol_html = '<span style="color: #8C8C8C; font-weight: bold;">{}</span>&nbsp;{}'
        symbol_list = [symbol_html.format(
            symbol[0],
            speech_html.format(b64encode_json(symbol[1]))
        ) for symbol in explanation.get('symbols', [])]
        symbol_contents = '&nbsp;&nbsp;&nbsp;'.join(symbol_list)
        if symbol_contents:
            explanation_list.append(explanation_html.format(symbol_contents))
        # 简明释义
        explain_html = '<span><i style="color: #8C8C8C;">{}</i><hr>{}</span>'
        explain_list = []
        for explain in explanation.get('explains', []):
            part = f"No.{explain['part']}" if isinstance(explain['part'], int) else explain['part']
            mean_list = []
            for index, mean in enumerate(explain['means']):
                span_html = '<span style="color: #8C8C8C;">{}</span>'
                a_html = '<a style="text-decoration: none; color: #506EFF;" href="#{}">{}</a>'
                text = a_html.format(b64encode_json(mean[0]), mean[0]) if mean[2] else mean[0]
                text_tr = span_html.format(mean[1]) if mean[1] else mean[1]
                if len(explain['means']) > 1 and mean[1]:
                    text_contents = f'<tr><td>{no_html.format(index + 1)}</td><td>&nbsp;</td><td>{text}</td></tr>' \
                                    f'<tr><td></td><td></td><td>{text_tr}</td></tr>'
                elif len(explain['means']) > 1:
                    text_contents = f'<tr><td>{no_html.format(index + 1)}</td><td>&nbsp;</td><td>{text}</td></tr>'
                elif mean[1]:
                    text_contents = f'<tr><td>{text}</td></tr>' \
                                    f'<tr><td>{text_tr}</td></tr>'
                else:
                    text_contents = f'<tr><td>{text}</td></tr>'
                mean_list.append(text_contents)
            mean_contents = f"<table>{''.join(mean_list)}</table>"
            explain_list.append(explain_html.format(part, mean_contents))
        explain_contents = '<br><br>'.join(explain_list)
        if explain_contents:
            explanation_list.append(explanation_html.format(explain_contents))
        if more:
            # 单词形态
            exchange_html = '<tr style="color: #8C8C8C;">' \
                            '<td>{}</td>' \
                            '<td>&nbsp;&nbsp;&nbsp;</td>' \
                            '<td><a style="text-decoration: none; color: #506EFF;" href="#{}">{}</a></td>' \
                            '</tr>'
            exchange_list = []
            for exchange in explanation.get('exchanges', []):
                exchange_list.append(exchange_html.format(
                    exchange['name'],
                    b64encode_json(exchange['value']),
                    exchange['value']
                ))
            if exchange_list:
                exchange_contents = f"<table>{''.join(exchange_list)}</table>"
                explanation_list.append(explanation_html.format(exchange_contents))
    if more:
        # 双语例句
        sentence_list = []
        sentences = obj.get_sentence(True)
        if len(sentences) > 3:
            # 例句数量大于3条时，随机选取其中3条例句
            sentences = random.sample(sentences, 3)
        for index, sentence in enumerate(sentences):
            no = no_html.format(index + 1)
            speech = speech_html.format(b64encode_json(sentence[2]))
            replace = '<b style="color: #F0374B;">'
            text = sentence[0].replace('<b>', replace)
            text_tr = sentence[1].replace('<b>', replace)
            if text_tr and sentence[3] == 1:
                text_contents = f'<tr><td>{no}</td><td>&nbsp;</td><td>{text}</td></tr>' \
                                f'<tr style="color: #8C8C8C;"><td></td><td></td><td>{text_tr}&nbsp;{speech}</td></tr>'
            elif text_tr and sentence[3] == 0:
                text_contents = f'<tr><td>{no}</td><td>&nbsp;</td><td>{text}&nbsp;{speech}</td></tr>' \
                                f'<tr style="color: #8C8C8C;"><td></td><td></td><td>{text_tr}</td></tr>'
            else:
                text_contents = f'<tr><td>{no}</td><td>&nbsp;</td><td>{text}&nbsp;{speech}</td></tr>'
            sentence_list.append(text_contents)
        if sentence_list:
            sentence_contents = f'<table>{"<hr width=0>".join(sentence_list)}</table>'
            explanation_list.append(explanation_html.format(sentence_contents))
    # 拼接HTML内容
    explanation_contents = '<hr width=0>'.join(explanation_list)

    return translation_contents, explanation_contents
