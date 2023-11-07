# -*- coding: utf-8 -*-
import json
import math
import re
from threading import Lock

from spider import BaseTranslate

# 百度翻译语言选项
baidu_lang = {
    '自动检测': '',
    '中文(简体)': 'zh',
    '英语': 'en',
    '日语': 'jp',
    '泰语': 'th',
    '西班牙语': 'spa',
    '阿拉伯语': 'ara',
    '法语': 'fra',
    '韩语': 'kor',
    '俄语': 'ru',
    '德语': 'de',
    '葡萄牙语': 'pt',
    '意大利语': 'it',
    '希腊语': 'el',
    '荷兰语': 'nl',
    '波兰语': 'pl',
    '芬兰语': 'fin',
    '捷克语': 'cs',
    '保加利亚语': 'bul',
    '丹麦语': 'dan',
    '爱沙尼亚语': 'est',
    '匈牙利语': 'hu',
    '罗马尼亚语': 'rom',
    '斯洛文尼亚语': 'slo',
    '瑞典语': 'swe',
    '越南语': 'vie',
    '中文(粤语)': 'yue',
    '中文(繁体)': 'cht',
    '中文(文言文)': 'wyw',
    '南非荷兰语': 'afr',
    '阿尔巴尼亚语': 'alb',
    '阿姆哈拉语': 'amh',
    '亚美尼亚语': 'arm',
    '阿萨姆语': 'asm',
    '阿斯图里亚斯语': 'ast',
    '阿塞拜疆语': 'aze',
    '巴斯克语': 'baq',
    '白俄罗斯语': 'bel',
    '孟加拉语': 'ben',
    '波斯尼亚语': 'bos',
    '缅甸语': 'bur',
    '加泰罗尼亚语': 'cat',
    '宿务语': 'ceb',
    '克罗地亚语': 'hrv',
    '世界语': 'epo',
    '法罗语': 'fao',
    '菲律宾语': 'fil',
    '加利西亚语': 'glg',
    '格鲁吉亚语': 'geo',
    '古吉拉特语': 'guj',
    '豪萨语': 'hau',
    '希伯来语': 'heb',
    '印地语': 'hi',
    '冰岛语': 'ice',
    '伊博语': 'ibo',
    '印尼语': 'id',
    '爱尔兰语': 'gle',
    '卡纳达语': 'kan',
    '克林贡语': 'kli',
    '库尔德语': 'kur',
    '老挝语': 'lao',
    '拉丁语': 'lat',
    '拉脱维亚语': 'lav',
    '立陶宛语': 'lit',
    '卢森堡语': 'ltz',
    '马其顿语': 'mac',
    '马拉加斯语': 'mg',
    '马来语': 'may',
    '马拉雅拉姆语': 'mal',
    '马耳他语': 'mlt',
    '马拉地语': 'mar',
    '尼泊尔语': 'nep',
    '新挪威语': 'nno',
    '波斯语': 'per',
    '萨丁尼亚语': 'srd',
    '塞尔维亚语(拉丁文)': 'srp',
    '僧伽罗语 ': 'sin',
    '斯洛伐克语': 'sk',
    '索马里语': 'som',
    '斯瓦希里语': 'swa',
    '他加禄语': 'tgl',
    '塔吉克语': 'tgk',
    '泰米尔语': 'tam',
    '鞑靼语': 'tat',
    '泰卢固语': 'tel',
    '土耳其语': 'tr',
    '土库曼语': 'tuk',
    '乌克兰语': 'ukr',
    '乌尔都语': 'urd',
    '奥克语': 'oci',
    '吉尔吉斯语': 'kir',
    '普什图语': 'pus',
    '高棉语': 'hkm',
    '海地语': 'ht',
    '书面挪威语': 'nob',
    '旁遮普语': 'pan',
    '阿尔及利亚阿拉伯语': 'arq',
    '比斯拉马语': 'bis',
    '加拿大法语': 'frn',
    '哈卡钦语': 'hak',
    '胡帕语': 'hup',
    '印古什语': 'ing',
    '拉特加莱语': 'lag',
    '毛里求斯克里奥尔语': 'mau',
    '黑山语': 'mot',
    '巴西葡萄牙语': 'pot',
    '卢森尼亚语': 'ruy',
    '塞尔维亚-克罗地亚语': 'sec',
    '西里西亚语': 'sil',
    '突尼斯阿拉伯语': 'tua',
    '亚齐语': 'ach',
    '阿肯语': 'aka',
    '阿拉贡语': 'arg',
    '艾马拉语': 'aym',
    '俾路支语': 'bal',
    '巴什基尔语': 'bak',
    '本巴语': 'bem',
    '柏柏尔语': 'ber',
    '博杰普尔语': 'bho',
    '比林语': 'bli',
    '布列塔尼语': 'bre',
    '切罗基语': 'chr',
    '齐切瓦语': 'nya',
    '楚瓦什语': 'chv',
    '康瓦尔语': 'cor',
    '科西嘉语': 'cos',
    '克里克语': 'cre',
    '克里米亚鞑靼语': 'cri',
    '迪维希语': 'div',
    '古英语': 'eno',
    '中古法语': 'frm',
    '弗留利语': 'fri',
    '富拉尼语': 'ful',
    '盖尔语': 'gla',
    '卢干达语': 'lug',
    '古希腊语': 'gra',
    '瓜拉尼语': 'grn',
    '夏威夷语': 'haw',
    '希利盖农语': 'hil',
    '伊多语': 'ido',
    '因特语': 'ina',
    '伊努克提图特语': 'iku',
    '爪哇语': 'jav',
    '卡拜尔语': 'kab',
    '格陵兰语': 'kal',
    '卡努里语': 'kau',
    '克什米尔语': 'kas',
    '卡舒比语': 'kah',
    '卢旺达语': 'kin',
    '刚果语': 'kon',
    '孔卡尼语': 'kok',
    '林堡语': 'lim',
    '林加拉语': 'lin',
    '逻辑语': 'loj',
    '低地德语': 'log',
    '下索布语': 'los',
    '迈蒂利语': 'mai',
    '曼克斯语': 'glv',
    '毛利语': 'mao',
    '马绍尔语': 'mah',
    '南恩德贝莱语': 'nbl',
    '那不勒斯语': 'nea',
    '西非书面语': 'nqo',
    '北方萨米语': 'sme',
    '挪威语': 'nor',
    '奥杰布瓦语': 'oji',
    '奥里亚语': 'ori',
    '奥罗莫语': 'orm',
    '奥塞梯语': 'oss',
    '邦板牙语': 'pam',
    '帕皮阿门托语': 'pap',
    '北索托语': 'ped',
    '克丘亚语': 'que',
    '罗曼什语': 'roh',
    '罗姆语': 'ro',
    '萨摩亚语': 'sm',
    '梵语': 'san',
    '苏格兰语': 'sco',
    '掸语': 'sha',
    '修纳语': 'sna',
    '信德语': 'snd',
    '桑海语': 'sol',
    '南索托语': 'sot',
    '叙利亚语': 'syr',
    '德顿语': 'tet',
    '提格利尼亚语': 'tir',
    '聪加语': 'tso',
    '契维语': 'twi',
    '高地索布语': 'ups',
    '文达语': 'ven',
    '瓦隆语': 'wln',
    '威尔士语': 'wel',
    '西弗里斯语': 'fry',
    '沃洛夫语': 'wol',
    '科萨语': 'xho',
    '意第绪语': 'yid',
    '约鲁巴语': 'yor',
    '扎扎其语': 'zaz',
    '祖鲁语': 'zul',
    '巽他语': 'sun',
    '苗语': 'hmn',
    '塞尔维亚语(西里尔文)': 'src'
}


def n(r: int, o: str):
    for t in range(0, len(o) - 2, 3):
        a = o[t + 2]
        a = ord(a[0]) - 87 if a >= 'a' else int(a)
        a = r >> a if '+' == o[t + 1] else r << a
        r = r + a & 4294967295 if '+' == o[t] else r ^ a
    return r


def e(r: str):
    i = '320305.131321201'
    o = re.findall('[\U00010000-\U0010ffff]', r)
    if not o:
        t = len(r)
        if t > 30:
            r = r[:10] + r[math.floor(t / 2) - 5: math.floor(t / 2) + 5] + r[-10:]
    else:
        e = re.split('[\U00010000-\U0010ffff]', r)
        h, f = len(e), []
        for C in range(0, h):
            if e[C]:
                f.extend(e[C])
            if C != h - 1:
                f.append(o[C])
        g = len(f)
        if g > 30:
            r = ''.join(f[:10] + f[math.floor(g / 2) - 5: math.floor(g / 2) + 5] + f[-10:])
    d = i.split('.')
    S, v = [], 0
    while v < len(r):
        A = ord(r[v])
        if 128 > A:
            S.append(A)
        elif 2048 > A:
            S.extend([A >> 6 | 192, 63 & A | 128])
        elif 55296 == (64512 & A) and v + 1 < len(r) and 56320 == (64512 & ord(r[v + 1])):
            A = 65536 + ((1023 & A) << 10) + (1023 & ord(r[++v]))
            S.extend([A >> 18 | 240, A >> 12 & 63 | 128, A >> 6 & 63 | 128, 63 & A | 128])
        else:
            S.extend([A >> 12 | 224, A >> 6 & 63 | 128, 63 & A | 128])
        v += 1
    m, s, F, D = int(d[0]) | 0, int(d[1]) | 0, '+-a^+6', '+-3^+b+-f'
    p = m
    for b in range(0, len(S)):
        p += S[b]
        p = n(p, F)
    p = n(p, D) ^ s
    if p < 0:
        p = (2147483647 & p) + 2147483648
    p = int(p % 1e6)
    return f'{p}.{p ^ m}'


class BaiduTranslate(BaseTranslate):
    """百度翻译爬虫"""
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
            super(BaiduTranslate, self).__init__()
            # 百度翻译主页
            self.home = 'https://fanyi.baidu.com/'
            # 请求一下首页以更新客户端的cookies
            self._get()
            # 获取token（必须先更新客户端的cookies，再次请求首页时才会有token）
            # 发送翻译请求时需携带此token
            response = self._get()
            self.token = re.findall(r'token:[\s\'"]+([a-z\d]+)[\'"],', response.text)[0]
            # 标记初始化完成
            self._init_flag = True

    def _get_lan(self, query):
        """查询语言种类"""
        path = 'langdetect'
        form_data = {
            'query': query,
        }
        response = self._post(path, form_data)
        content = json.loads(response.content)
        return content.get('lan')

    def _get_form_data(self, query, from_lan, to_lan):
        """构建表单数据"""
        # with open(index_d52622f_js, 'r', encoding='UTF-8') as f:
        #     js = f.read()
        # eval_js = js2py.eval_js(js)
        # sign = eval_js(query)
        sign = e(query)
        form_data = {
            'to': to_lan,
            'from': from_lan,
            'query': query,
            'sign': sign,
            'token': self.token,
        }
        return form_data

    def translate(self, query, to_lan, from_lan=None, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        if not from_lan:
            from_lan = self._get_lan(query)  # 自动检测源语言
        if from_lan == to_lan:
            to_lan = 'en' if from_lan == 'zh' else 'zh'
        path = 'v2transapi'
        params = {'from': from_lan, 'to': to_lan}
        form_data = self._get_form_data(query, from_lan, to_lan)
        headers = {'Acs-Token': '400'}  # TODO 新增的请求头。服务端尚未做校验，暂时为空
        response = self._post(path, form_data, params=params, headers=headers)
        data = response.json()
        assert data.get('errno') is None, f'翻译失败！（{data["errno"]}，{data["errmsg"]}）'
        self.data = data
        self.from_lan = from_lan
        self.to_lan = to_lan

    def get_translation(self, *args, **kwargs):
        """ 获取译文
        ["你好", ["你好", "zh"]]
        """
        translation_data = []
        dst = '\n'.join([data['dst'] for data in self.data['trans_result']['data']])
        translation_data.append(dst)
        translation_data.append([dst, self.data['trans_result']['to']])
        return translation_data

    def get_explanation(self, *args, **kwargs):
        """ 获取释义
        [{
            "symbols": [
                ["英 [həˈləʊ]", ["hello", "uk"]],
                ["美 [heˈloʊ]", ["hello", "en"]]
            ],
            "explains": [
                {
                    "part": "int./n",
                    "means": [
                        ["你好；(用于问候、接电话或引起注意)喂；(表示惊讶或认为别人说了蠢话或没有注意听)嘿", "", False]
                    ]
                }
            ],
            "exchanges": [
                {
                    "name": "复数",
                    "value": "hellos"
                }
            ]
        }]
        """
        explanation_data = []
        simple_means = self.data.get('dict_result', {}).get('simple_means')
        if simple_means:
            symbols = simple_means['symbols'][0]
            # 解析音标
            symbol_list = []
            if symbols.get('word_symbol'):
                symbol_list.append([f'音 [{symbols["word_symbol"]}]', [simple_means["word_name"], 'zh']])
            if symbols.get('ph_en'):
                symbol_list.append([f'英 [{symbols["ph_en"]}]', [simple_means["word_name"], 'uk']])
            if symbols.get('ph_am'):
                symbol_list.append([f'美 [{symbols["ph_am"]}]', [simple_means["word_name"], 'en']])
            # 解析释义
            explain_list = []
            for index, parts in enumerate(symbols['parts']):
                if isinstance(parts['means'][0], dict):
                    for index2, mean in enumerate(parts['means']):
                        part = index2 + 1
                        means = [[mean['text'], '；'.join(mean.get('means', [])), True]]
                        explain_list.append({'part': part, 'means': means})
                else:
                    part = parts.get('part') or parts.get('part_name') or index + 1
                    means = [['；'.join(parts['means']), '', False]]
                    explain_list.append({'part': part, 'means': means})
            # 解析形态
            exchange_list = []
            exchange_dict = {
                'word_third': '第三人称单数',
                'word_pl': '复数',
                'word_ing': '现在分词',
                'word_done': '过去式',
                'word_past': '过去分词',
                'word_er': '比较级',
                'word_est': '最高级',
                'word_proto': '原形',
            }
            exchange = simple_means.get('exchange', {})
            for k, v in exchange.items():
                if v:
                    exchange_list.append({'name': exchange_dict.get(k), 'value': v[0]})
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list, 'exchanges': exchange_list})
        return explanation_data

    def get_sentence(self, *args, **kwargs):
        """ 获取例句
        [
            [
                "‘ Oh, hello, ’ he said, with a smile.",
                "“嗨，你好。”他微笑着说。",
                ["‘ Oh, hello, ’ he said, with a smile.", "en"],
                0
            ],
            [
                "Hello, Mr Brown.",
                "你好，布朗先生。",
                ["Hello, Mr Brown.", "en"],
                0
            ]
        ]
        """
        sentence_data = []
        from_lan = self.data['trans_result']['from']
        double_list = json.loads(self.data['liju_result']['double']) if self.data['liju_result']['double'] else []
        for double in double_list:
            # 解析例句
            sentence = ''
            sentence_text = ''
            for item in double[0]:
                string = f'<b>{item[0]}</b>' if item[3] == 1 else item[0]  # 标记查询的单词
                sentence += string + (item[-1] if len(item) == 5 else '')
                sentence_text += item[0] + (item[-1] if len(item) == 5 else '')
            # 解析例句翻译
            sentence_tr = ''
            for item in double[1]:
                sentence_tr += item[0] + (item[-1] if len(item) == 5 else '')
            # 构建例句 TTS 获取参数
            sentence_speech = [sentence_text if from_lan == 'en' else sentence_tr, 'en']
            sentence_data.append([sentence, sentence_tr, sentence_speech, 0 if from_lan == 'en' else 1])
        return sentence_data

    def get_tts(self, text, lan, *args, **kwargs):
        """ 获取发音

        :param text: 源文本
        :param lan: 文本语言
        :return: 文本语音
        """
        spd = 5 if lan == 'zh' else 3
        path = 'gettts'
        params = {'lan': lan, 'text': text, 'spd': spd, 'source': 'web'}
        response = self._get(path, params)
        content = response.content
        return content

    def get_ocr(self, img, from_lan=None, *args, **kwargs):
        """ 从图片中提取文字(精度差)
        识别结果为空时，可尝试切换识别语言
        """
        path = 'getocr'
        form_data = {'from': from_lan or 'auto', 'to': 'zh'}
        files = {'image': img}
        response = self._post(path, form_data, files)
        data = response.json().get('data') or {}
        src = ' '.join(data.get('src', []))
        return src


if __name__ == '__main__':
    bt = BaiduTranslate()
    bt.translate('hello', 'zh')
    translations = bt.get_translation()
    explanations = bt.get_explanation()
    tts = bt.get_tts(*explanations[0]['symbols'][0][1])
    sentences = bt.get_sentence()
    print(bt.data)
