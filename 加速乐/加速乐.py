import requests
import execjs
import re


class JiaSuLe:
    def __init__(self, url):
        self.url = url
        self.s = requests.session()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'bj.gsxt.gov.cn',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        }

    def get_cookies(self):
        '''

        :return: cookies
        '''
        res = self.s.get(self.url, headers=self.headers)
        get_cookie_js_1 = 'function f() {return ' + res.text[24:-56] + '}'
        cookies_1 = res.headers.get('Set-Cookie')
        request_2_cookies = self.js_res(get_cookie_js_1, 'f') + ';' + cookies_1
        self.headers.update({'Cookie': request_2_cookies})

        res = self.s.get(self.url, headers=self.headers)
        # 处理动态js
        js_header = '''document = new Object();location = new Object();window = {};var navigator = new Object();navigator.userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36";window.navigator = navigator;'''
        cookie2_js = re.search('<script>(.*?)</script>', res.text, re.S).group(1)
        cookie2_js = js_header + cookie2_js
        create_cookies = re.search("setTimeout.*?document.*?'ie'\]=(.*?);", cookie2_js).group(1)
        cookie2_js = cookie2_js.replace('};go', f'return {create_cookies}}};go')
        cookie2_js = cookie2_js.replace(';go', ';function cookie() {return go') + '}'
        print(cookie2_js)
        # cookie2_js = re.sub("setTimeout,function\(\)\{document\[.*?\},(,*?)\); \1","setTimeout,0,",cookie2_js)
        # print(cookie2_js)
        cookie2 = self.js_res(cookie2_js, 'cookie')
        request_3_cookies = cookies_1 + ';' + cookie2
        self.headers.update({'Cookie': request_3_cookies})

    def js_res(self, js_str, fun_name):
        '''

        :param js_str: js代码
        :param fun_name: 执行方法名
        :return: js执行结果
        '''
        js_data = execjs.compile(js_str)
        if fun_name:
            return js_data.call(fun_name)

    def get_content(self):
        self.get_cookies()
        res = self.s.get(self.url, headers=self.headers).text
        return res


if __name__ == '__main__':
    J = JiaSuLe('http://bj.gsxt.gov.cn/index.html')
    J.get_content()
