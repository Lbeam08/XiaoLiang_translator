# -*- coding: utf-8 -*-
from spider.transl_baidu import baidu_lang, BaiduTranslate
from spider.transl_google import google_lang, GoogleTranslate
from spider.transl_sougou import sougou_lang, SougouTranslate
from spider.transl_youdao import youdao_lang, YoudaoTranslate

# 翻译引擎名称
engine_name = {
    '百度翻译': 'baidu',
    '有道词典': 'youdao',
    '搜狗翻译': 'sougou',
    '谷歌翻译': 'google',
}

# 翻译引擎语言
engine_lang = {
    'baidu': baidu_lang,
    'youdao': youdao_lang,
    'sougou': sougou_lang,
    'google': google_lang
}

# 翻译引擎类
engine_class = {
    'baidu': BaiduTranslate,
    'youdao': YoudaoTranslate,
    'sougou': SougouTranslate,
    'google': GoogleTranslate
}
