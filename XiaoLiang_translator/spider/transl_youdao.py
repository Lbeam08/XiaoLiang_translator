# -*- coding: utf-8 -*-
from hashlib import md5
from threading import Lock
from urllib.parse import parse_qs

from spider import BaseTranslate

# 有道词典语言选项
youdao_lang = {
    '自动检测语言': '',
    '中英': 'en',
    '中法': 'fr',
    '中韩': 'ko',
    '中日': 'ja',
}


class YoudaoTranslate(BaseTranslate):
    """有道词典爬虫"""
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
            super(YoudaoTranslate, self).__init__()
            # 有道词典主页
            self.home = 'https://dict.youdao.com/'
            # 请求一下首页以更新客户端的cookies
            self._get()
            # 中日互译时如果有两种结果，则该标志为 True
            self.reverse_flag = False
            # 标记初始化完成
            self._init_flag = True

    @staticmethod
    def _get_form_data(text, le):
        """构建表单参数"""
        v = 'Mk6hqtUp33DGGtoS63tTJbMUYjRrG1Lu'
        _ = 'webdict'
        x = 'web'

        r = text + _
        time = len(r) % 10
        n = md5(r.encode('utf-8')).hexdigest()
        o = x + text + str(time) + v + n
        f = md5(o.encode('utf-8')).hexdigest()

        form_data = {
            'q': text,
            'le': le,
            't': time,
            'client': x,
            'sign': f,
            'keyfrom': _,
        }
        return form_data

    def translate(self, query, to_lan, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param to_lan: 源语言
        :return:
        """
        form_data = self._get_form_data(query, to_lan)
        path = 'jsonapi_s'
        params = {'doctype': 'json', 'jsonversion': 4}
        response = self._post(path, form_data, params=params)
        data = response.json()
        assert data.get('code') is None, f'翻译失败！（{data["code"]}，{data["message"]}）'
        self.data = data
        if to_lan == 'ja':  # 【中日】互译时检查是否有两种结果
            newjc = self.data.get('newjc', {}).get('word')
            cj = self.data.get('cj', {}).get('word')
            self.reverse_flag = newjc and cj
        self.to_lan = to_lan

    def get_translation(self, *args, **kwargs):
        """ 获取译文
        ["hello", ["hello", "eng"]]
        """
        translation_data = []
        if self.data.get('fanyi'):
            to_str = self.data['fanyi']['type'].split('2')[-1].split('-')[0]
            translation_data.append(self.data['fanyi']['tran'])
            translation_data.append([self.data['fanyi']['tran'], to_str])
        else:
            translation_data.append(self.data['meta']['input'])
            translation_data.append([self.data['meta']['input'], self.data['meta']['guessLanguage']])
        return translation_data

    def get_explanation(self, reverse=False, *args, **kwargs):
        """ 获取释义
        [{
            "symbols": [
                ["英 [həˈləʊ]", ["hello", "", 1]],
                ["美 [heˈloʊ]", ["hello", "", 2]]
            ],
            "explains": [
                {
                    "part": "int.",
                    "means": [
                        ["喂，你好（用于问候或打招呼）；喂，你好（打电话时的招呼语）；喂，你好（引起别人注意的招呼语）", "", False]
                    ]
                },
                {
                    "part": "n.",
                    "means": [
                        ["招呼，问候；（Hello）（法、印、美、俄）埃洛（人名）", "", False]
                    ]
                }
            ],
            "exchanges": [
                {
                    "name": "复数",
                    "value": "hellos"
                },
                {
                    "name": "过去式",
                    "value": "helloed"
                }
            ]
        }]
        """
        input_text = self.data['meta']['input']
        guess_language = self.data['meta']['guessLanguage']
        explanation_data = []
        if self.data.get('fanyi'):
            return explanation_data
        # 【中英】翻译结果解析
        elif self.data.get('le') == 'en' and self.data.get('ce', self.data.get('ec')):
            word = self.data.get('ce', self.data.get('ec')).get('word', {})
            # 解析音标
            symbol_list = []
            if word.get('phone'):
                symbol_list.append([f'音 [{word["phone"]}]', [input_text, guess_language]])
            if word.get("ukphone"):
                symbol_list.append([f'英 [{word["ukphone"]}]', [input_text, guess_language, 1]])
            if word.get("usphone"):
                symbol_list.append([f'美 [{word["usphone"]}]', [input_text, guess_language]])
            # 解析释义
            explain_list = []
            for index, trs in enumerate(word.get('trs', [])):
                b = trs.get('#text') is not None  # 「中 > 英」标记
                explain_list.append({
                    'part': trs.get('pos') or index + 1,
                    'means': [[trs.get('tran', trs.get('#text')), trs.get('#tran', ''), b]]
                })
            # 解析形态
            exchange_list = [item['wf'] for item in word.get('wfs', [])]
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list, 'exchanges': exchange_list})
        # 【中法】翻译结果解析
        elif self.data.get('le') == 'fr' and self.data.get('cf', self.data.get('fc')):
            word = self.data.get('cf', self.data.get('fc'))['word'][0]
            # 解析音标
            symbol_list = []
            if word.get('phone'):
                symbol_list.append([f'音 [{word["phone"]}]', [input_text, guess_language]])
            # 解析释义
            explain_list = []
            if self.data.get('cf'):  # 中 > 法
                for index, tr in enumerate(word['trs'][0]['tr']):
                    explain_list.append({'part': index + 1, 'means': [[tr['l']['i'][0], '', True]]})
            elif self.data.get('fc'):  # 法 > 中
                for trs in word['trs']:
                    explain_list.append({'part': trs['pos'], 'means': [[trs['tr'][0]['l']['i'][0], '', False]]})
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list})
        # 【中韩】翻译结果解析
        elif self.data.get('le') == 'ko' and self.data.get('ck', self.data.get('kc')):
            word = self.data.get('ck', self.data.get('kc'))['word']
            # 解析音标
            symbol_list = []
            if word[0].get('phone'):
                symbol_list.append([f'音 [{word[0]["phone"]}]', [input_text, guess_language]])
            # 解析释义
            explain_list = []
            if self.data.get('ck'):  # 中 > 韩
                num = 1
                for trs in word[0]['trs']:
                    pos = trs.get('pos')
                    if pos is None:
                        for tr in trs['tr']:
                            pos = num
                            num += 1
                            explain_list.append({'part': pos, 'means': [[tr['l']['i'][0], '', False]]})
                    else:
                        explain_list.append({'part': pos, 'means': [[trs['tr'][0]['l']['i'][0], '', False]]})
            elif self.data.get('kc'):  # 韩 > 中
                for item in word:
                    for index, trs in enumerate(item['trs']):
                        tr_list = [[tr['l']['i'][0], '', False] for tr in trs['tr']]
                        explain_list.append({'part': trs.get('pos') or index + 1, 'means': tr_list})
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list})
        # 【中日】翻译结果解析
        elif self.data.get('le') == 'ja':
            newjc = self.data.get('newjc', {}).get('word')
            cj = self.data.get('cj', {}).get('word')
            newjc_data = []  # 「日 > 中」数据
            cj_data = []  # 「中 > 日」数据

            def get_word(word_, tag=False):
                # 解析音标
                head = word_['head']
                symbol_list = []
                to_str = head['type'].split('2')[0].split('-')[0]
                text = head.get('pjm', head.get('hw'))
                if head.get('rs'):
                    symbol_list.append([f'{head["pjm"]} [{head["rs"]}]', [text, to_str]])
                if head.get('sound'):
                    symbol_list.append([f'音 [{head["sound"]}]', [text, to_str]])
                # 解析释义
                num = 1
                explain_list = []
                for sense in word_['sense']:
                    cx = sense.get('cx') or num
                    jmsy_list = [[phrList['jmsy'], phrList.get('jmsyT', ''), tag] for phrList in sense['phrList']]
                    explain_list.append({'part': cx, 'means': jmsy_list})
                    num += 1
                # 返回数据
                return {'symbols': symbol_list, 'explains': explain_list}

            # 解析翻译结果
            if newjc:  # 日 > 中
                word_data = get_word(newjc)
                newjc_data.append(word_data)
                # 同一个词语有多个读音和释义
                for mPhonicD in newjc.get('mPhonicD', []):
                    word_data = get_word(mPhonicD)
                    newjc_data.append(word_data)
            if cj:  # 中 > 日
                word_data = get_word(cj, True)
                cj_data.append(word_data)

            # 【中日】互译时如果有两个结果：
            # 1. 默认返回「中 > 日」结果
            # 2. 参数 reverse=True 时返回「日 > 中」结果
            if newjc and cj:
                explanation_data = newjc_data if reverse else cj_data
            else:
                explanation_data = newjc_data or cj_data

        return explanation_data

    def get_sentence(self, more=False, *args, **kwargs):
        """ 获取例句
        [
            [
                "'Hello, Paul,' they chorused.",
                "“你好，保罗。”他们齐声问候道。",
                ["'Hello, Paul,' they chorused.", "eng"],
                0
            ],
            [
                "Hello, this is John Thompson.",
                "你好，我是约翰·汤普森。",
                ["Hello, this is John Thompson.", "eng"],
                0
            ]
        ]
        """
        sentence_data = []
        if more:
            query = f'lj:{self.data["meta"]["input"]}'
            le = self.data['meta']['le']
            form_data = self._get_form_data(query, le)
            path = 'jsonapi_s'
            params = {'doctype': 'json', 'jsonversion': 4}
            response = self._post(path, form_data, params=params)
            body = response.json()
            sentence_pair = body.get('blng_sents', {}).get('sentence-pair', [])
        else:
            sentence_pair = self.data.get('blng_sents_part', {}).get('sentence-pair', [])
        for item in sentence_pair:
            # 补全获取例句语音的参数，然后再通过 urllib.parse.parse_qs 解析参数
            speech = parse_qs('audio=' + item.get('sentence-speech', item.get('sentence-translation-speech')))
            sentence_data.append([
                item.get('sentence-eng', item.get('sentence')),  # 例句
                item.get('sentence-translation'),  # 例句翻译
                [speech.get('audio', [''])[0], speech.get('le', [''])[0]],  # 例句语音获取参数
                0 if item.get('sentence-speech') else 1  # 标记发音句子的位置
            ])
        return sentence_data

    def get_tts(self, text, lan='', type_=2, *args, **kwargs):
        """ 获取发音

        :param text: 源文本
        :param lan: 文本语言
        :param type_: 发音类型
        :return: 文本语音
        """
        path = 'dictvoice'
        params = {'audio': text, 'le': lan, 'type': type_}
        response = self._get(path, params)
        content = response.content
        return content


if __name__ == '__main__':
    yt = YoudaoTranslate()
    yt.translate('hello', 'en')
    translations = yt.get_translation()
    explanations = yt.get_explanation()
    tts = yt.get_tts(*explanations[0]['symbols'][0][1])
    sentences = yt.get_sentence(True)
    print(yt.data)
