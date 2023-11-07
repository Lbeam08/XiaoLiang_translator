from abc import ABCMeta, abstractmethod

import httpx
from retrying import retry


class BaseTranslate(metaclass=ABCMeta):
    """翻译爬虫的基类"""

    def __init__(self):
        # 创建客户端并设置客户端UA
        self.session = httpx.Client(verify=False)
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                                             'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                             'Chrome/111.0.0.0 Safari/537.36'
        # 主页
        self.home = None
        # 翻译结果
        self.data = None
        # 源语言和目标语言
        self.from_lan = None
        self.to_lan = None

    @retry(stop_max_attempt_number=3)
    def _post(self, path='', data=None, files=None, json=None, params=None, headers=None):
        """发送 POST 请求"""
        url = self.home + path
        response = self.session.post(url, data=data, files=files, json=json, params=params, headers=headers)
        assert response.status_code == 200, f'请求失败！URL：{response.url}；状态码：{response.status_code}。'
        return response

    @retry(stop_max_attempt_number=3)
    def _get(self, path='', params=None, headers=None):
        """发送 GET 请求"""
        url = self.home + path
        response = self.session.get(url, params=params, headers=headers)
        assert response.status_code == 200, f'请求失败！URL：{response.url}；状态码：{response.status_code}。'
        return response

    @abstractmethod
    def translate(self, query, from_lan, to_lan, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        pass

    @abstractmethod
    def get_translation(self, *args, **kwargs):
        """获取译文"""
        pass

    @abstractmethod
    def get_explanation(self, *args, **kwargs):
        """获取释义"""
        pass

    @abstractmethod
    def get_sentence(self, *args, **kwargs):
        """获取例句"""
        pass

    @abstractmethod
    def get_tts(self, text, lan, *args, **kwargs) -> bytes:
        """ 获取发音

        :param text: 源文本
        :param lan: 文本语言
        :return: 文本语音
        """
        pass
