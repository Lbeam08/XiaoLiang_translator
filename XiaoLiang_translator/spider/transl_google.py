# -*- coding: utf-8 -*-
import base64
import json
from contextlib import suppress
from threading import Lock

from spider import BaseTranslate

# 谷歌翻译语言选项
google_lang = {
    '检测语言': 'auto',
    '阿尔巴尼亚语': 'sq',
    '阿拉伯语': 'ar',
    '阿姆哈拉语': 'am',
    '阿萨姆语': 'as',
    '阿塞拜疆语': 'az',
    '埃维语': 'ee',
    '艾马拉语': 'ay',
    '爱尔兰语': 'ga',
    '爱沙尼亚语': 'et',
    '奥利亚语': 'or',
    '奥罗莫语': 'om',
    '巴斯克语': 'eu',
    '白俄罗斯语': 'be',
    '班巴拉语': 'bm',
    '保加利亚语': 'bg',
    '冰岛语': 'is',
    '波兰语': 'pl',
    '波斯尼亚语': 'bs',
    '波斯语': 'fa',
    '博杰普尔语': 'bho',
    '布尔语': 'af',
    '鞑靼语': 'tt',
    '丹麦语': 'da',
    '德语': 'de',
    '迪维希语': 'dv',
    '蒂格尼亚语': 'ti',
    '多格来语': 'doi',
    '俄语': 'ru',
    '法语': 'fr',
    '梵语': 'sa',
    '菲律宾语': 'tl',
    '芬兰语': 'fi',
    '弗里西语': 'fy',
    '高棉语': 'km',
    '格鲁吉亚语': 'ka',
    '贡根语': 'gom',
    '古吉拉特语': 'gu',
    '瓜拉尼语': 'gn',
    '哈萨克语': 'kk',
    '海地克里奥尔语': 'ht',
    '韩语': 'ko',
    '豪萨语': 'ha',
    '荷兰语': 'nl',
    '吉尔吉斯语': 'ky',
    '加利西亚语': 'gl',
    '加泰罗尼亚语': 'ca',
    '捷克语': 'cs',
    '卡纳达语': 'kn',
    '科西嘉语': 'co',
    '克里奥尔语': 'kri',
    '克罗地亚语': 'hr',
    '克丘亚语': 'qu',
    '库尔德语（库尔曼吉语）': 'ku',
    '库尔德语（索拉尼）': 'ckb',
    '拉丁语': 'la',
    '拉脱维亚语': 'lv',
    '老挝语': 'lo',
    '立陶宛语': 'lt',
    '林格拉语': 'ln',
    '卢干达语': 'lg',
    '卢森堡语': 'lb',
    '卢旺达语': 'rw',
    '罗马尼亚语': 'ro',
    '马尔加什语': 'mg',
    '马耳他语': 'mt',
    '马拉地语': 'mr',
    '马拉雅拉姆语': 'ml',
    '马来语': 'ms',
    '马其顿语': 'mk',
    '迈蒂利语': 'mai',
    '毛利语': 'mi',
    '梅泰语（曼尼普尔语）': 'mni-Mtei',
    '蒙古语': 'mn',
    '孟加拉语': 'bn',
    '米佐语': 'lus',
    '缅甸语': 'my',
    '苗语': 'hmn',
    '南非科萨语': 'xh',
    '南非祖鲁语': 'zu',
    '尼泊尔语': 'ne',
    '挪威语': 'no',
    '旁遮普语': 'pa',
    '葡萄牙语': 'pt',
    '普什图语': 'ps',
    '齐切瓦语': 'ny',
    '契维语': 'ak',
    '日语': 'ja',
    '瑞典语': 'sv',
    '萨摩亚语': 'sm',
    '塞尔维亚语': 'sr',
    '塞佩蒂语': 'nso',
    '塞索托语': 'st',
    '僧伽罗语': 'si',
    '世界语': 'eo',
    '斯洛伐克语': 'sk',
    '斯洛文尼亚语': 'sl',
    '斯瓦希里语': 'sw',
    '苏格兰盖尔语': 'gd',
    '宿务语': 'ceb',
    '索马里语': 'so',
    '塔吉克语': 'tg',
    '泰卢固语': 'te',
    '泰米尔语': 'ta',
    '泰语': 'th',
    '土耳其语': 'tr',
    '土库曼语': 'tk',
    '威尔士语': 'cy',
    '维吾尔语': 'ug',
    '乌尔都语': 'ur',
    '乌克兰语': 'uk',
    '乌兹别克语': 'uz',
    '西班牙语': 'es',
    '希伯来语': 'iw',
    '希腊语': 'el',
    '夏威夷语': 'haw',
    '信德语': 'sd',
    '匈牙利语': 'hu',
    '修纳语': 'sn',
    '亚美尼亚语': 'hy',
    '伊博语': 'ig',
    '伊洛卡诺语': 'ilo',
    '意大利语': 'it',
    '意第绪语': 'yi',
    '印地语': 'hi',
    '印尼巽他语': 'su',
    '印尼语': 'id',
    '印尼爪哇语': 'jw',
    '英语': 'en',
    '约鲁巴语': 'yo',
    '越南语': 'vi',
    '中文（繁体）': 'zh-TW',
    '中文（简体）': 'zh-CN',
    '宗加语': 'ts',
}


class GoogleTranslate(BaseTranslate):
    """谷歌翻译爬虫"""
    _lock = Lock()
    _instance = None
    _init_flag = False

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._init_flag:  # 只初始化一次
            super(GoogleTranslate, self).__init__()
            # 谷歌翻译主页
            self.home = 'https://translate.google.com/'
            # 请求一下首页以更新客户端的cookies
            self._get()
            # 标记初始化完成
            self._init_flag = True

    @staticmethod
    def _get_form_data(rpcids, query, from_lan, to_lan=None):
        """构建表单参数"""
        list_ = [query, from_lan, to_lan, bool(to_lan) or None]
        if to_lan:
            list_ = [list_, [None]]
        form_data = {'f.req': json.dumps([[[rpcids, json.dumps(list_), None, "generic"]]])}
        return form_data

    def translate(self, query, from_lan, to_lan, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        rpcids = 'MkEWBc'
        form_data = self._get_form_data(rpcids, query, from_lan, to_lan)
        path = '_/TranslateWebserverUi/data/batchexecute'
        response = self._post(path, form_data)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        self.data = data
        self.from_lan = from_lan
        self.to_lan = to_lan

    def get_translation(self, *args, **kwargs):
        """ 获取译文
        ["你好", ["你好", "zh"]]
        """
        translation_data = []
        with suppress(IndexError, TypeError):
            text = self.data[1][0][0][5][0][0]
            translation_data.append(text)
            translation_data.append([text, self.data[1][1]])
        return translation_data

    def get_explanation(self, *args, **kwargs):
        """ 获取释义
        [{
            "symbols": [
                ["音 [ɡo͝od]", ["good", "en"]]
            ],
            "explains": [
                {
                    "part": "形容词",
                    "means": [
                        ["好", "good", False],
                        ["良好", "good, well, favorable, fine, favourable", True]
                    ]
                },
                {
                    "part": "名词",
                    "means": [
                        ["益处", "benefit, good, profit", False],
                        ["甜头", "good, sweet taste, pleasant flavor", True]
                    ]
                }
            ]
        }]
        """
        explanation_data = []
        with suppress(IndexError, TypeError):
            # 解析音标和释义
            symbol_list, explain_list = [], []
            symbol_list.append([f'音 [{self.data[0][0]}]', [self.data[0][4][0][0], self.data[0][2]]])
            for i in self.data[3][5][0]:
                explain_list.append({'part': i[0], 'means': [[n[0], '；'.join(n[2]), True] for n in i[1]]})
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list})
        return explanation_data

    def get_sentence(self, *args, **kwargs):
        """ 获取例句
        [
            [
                "hello there, Katie!",
                "",
                ["hello there, Katie!", "en"],
                0
            ]
        ]
        """
        sentence_data = []
        with suppress(IndexError, TypeError):
            sentence_pair = self.data[3][2][0]
            for item in sentence_pair:
                sentence_data.append([item[1], '', [item[1], 'en'], 0])
        return sentence_data

    def get_tts(self, text, lan, *args, **kwargs):
        """获取发音"""
        rpcids = 'jQ1olc'
        form_data = self._get_form_data(rpcids, text, lan)
        path = '_/TranslateWebserverUi/data/batchexecute'
        response = self._post(path, form_data)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        return base64.b64decode(data[0])


if __name__ == '__main__':
    gt = GoogleTranslate()
    gt.translate('hello', 'auto', 'zh-CN')
    translations = gt.get_translation()
    explanations = gt.get_explanation()
    tts = gt.get_tts(*explanations[0]['symbols'][0][1])
    sentences = gt.get_sentence()
    print(gt.data)
