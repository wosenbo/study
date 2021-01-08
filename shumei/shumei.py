import requests
import re
import random
import json
import base64
import cv2
import time
from Crypto.Cipher import DES


def encrypt(key, text):
    """
    DES 加密
    :param key: 密钥, 长度必须为 16(AES-128)、24(AES-192)、32(AES-256) Bytes 长度
    :param text: 密文
    :return:
    """
    encrypter = DES.new(key.encode(), DES.MODE_ECB)
    length = 8
    count = len(text)
    if count < length:
        add = (length - count)
        text = text + ('\0' * add)
    elif count > length:
        add = (length - (count % length))
        text = text + ('\0' * add)
    ciphertext = encrypter.encrypt(text.encode())
    return base64.b64encode(ciphertext)


def decrypt(key, text):
    """
    DES 解密
    :param key: 密钥
    :param text: 密文
    :return:
    """
    decrypter = DES.new(key.encode(), DES.MODE_ECB)
    return decrypter.decrypt(text).decode('utf-8')


def des_res(key, text):
    return encrypt(decrypt("sshummei", base64.b64decode(key))[:8], text).decode()


class ShuMei():
    '''
    响应体riskLevel为pass即验证成功
    '''
    def __init__(self):
        self.register_url = "https://captcha.fengkongcloud.com/ca/v1/register"
        self.fverify_url = "https://captcha.fengkongcloud.com/ca/v2/fverify"
        self.img_url = "https://castatic.fengkongcloud.com"
        self.header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'captcha.fengkongcloud.com',
            'Referer': 'https://www.ishumei.com/trial/captcha.html',
            'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        }

        self.imgs_path = ['bg.jpg','fg.png']

    def get_organization(self):
        url = "https://www.ishumei.com/trial/captcha.html"
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'})
        organization = re.search('organization:"(.*?)"', res.text).group(1)
        print(f"organization:{organization}")
        return organization

    def get_register_data(self):
        data = {
            'sdkver': '1.1.3',
            'channel': 'DEFAULT',
            'rversion': '1.0.3',
            'model': 'slide',
            'lang': 'zh-cn',
            'data': '{}',
            'appId': 'default',
            'callback': f'sm_{int((time.time())*1000)}',
            'organization': 'RlokQwRlVjUrTUlkIqOg',
        }
        res = requests.get(url=self.register_url, headers=self.header, params=data)
        register_data = re.search("sm_\d+\((.*?)\)", res.text).group(1)
        register_data = json.loads(register_data)
        print(register_data)
        return register_data['detail']

    def save_img(self,img_urls):

        for i in range(2):

            res = requests.get(self.img_url + img_urls[i])
            print(self.img_url + img_urls[i])
            with open(self.imgs_path[i],'wb',) as f_wb:
                f_wb.write(res.content)
                print(f'{self.imgs_path[i]}图已保存')

    def img_distance(self):
        target = self.imgs_path[0]
        template = self.imgs_path[1]
        target_rgb = cv2.imread(target)
        target_gray = cv2.cvtColor(target_rgb, cv2.COLOR_BGR2GRAY)
        template_rgb = cv2.imread(template, 0)
        res = cv2.matchTemplate(target_gray, template_rgb, cv2.TM_CCOEFF_NORMED)
        value = cv2.minMaxLoc(res)
        distance = value[3][0] + 7
        print(f"滑块距离：{distance/2}")
        return int(distance/2)

    def generate_trajectory(self,dis):
        '''
        :param dis:移动距离
        :return: 轨迹数组
        [横坐标,纵坐标,时间10ms累加]
        '''
        tra_list = []
        x = 0
        y = 0
        t = 0
        tra_list.append([x,y,t])
        while 1:
            x += random.randint(0,30)
            y += random.randint(-5,5)
            t += random.randint(95,105)
            if x < dis:
                tra_list.append([x,y,t])
            else:
                tra_list.append([dis,y,t])
                break
        print(f"轨迹数组:{tra_list}")
        return tra_list

    def get_par_name(self):
        url = "https://castatic.fengkongcloud.com/pr/auto-build/v1.0.3-66/captcha-sdk.min.js"
        res = requests.get(url,).text
        par_names = re.search("_0x402c\('0x3fd'\),(.*?)'gifnoc_",res).group(1)
        par_name = par_names.split(',')
        del par_name[3]
        del par_name[-1]
        print(par_name)
        par_name = [i.replace("'",'',2)[::-1] for i in par_name]
        print('参数:',par_name)
        return par_name

    def get_ver_params(self, img_urls):

        distance = self.img_distance()
        trajectory = self.generate_trajectory(distance)
        par_name = self.get_par_name()
        ver_params = {
            par_name[3]: distance / 300,
            par_name[4]: trajectory,
            par_name[5]: random.randint(2700, 3500),
            par_name[6]: 300,
            par_name[7]: 150,
            par_name[8]: "web_pc",
            par_name[9]: 1,
            par_name[10]: 0,
            par_name[11]: -1,
            par_name[0]: 'default',
            par_name[1]: 'DEFAULT',
            par_name[2]: 'zh-cn',
        }
        # ver_params = {
        #     'an': distance / 300,
        #     'ln': trajectory,
        #     'mq': random.randint(2700, 3500),
        #     'sg': 300,
        #     'pr': 150,
        #     'act.os': "web_pc",
        #     'kh': 1,
        #     'xm': 0,
        #     'xs': -1,
        #     'ta': 'default',
        #     'tq': 'DEFAULT',
        #     'va': 'zh-cn',
        # }
        print(f"ver_params:{ver_params}")
        return ver_params

    def enc_params(self,key,params):
        enc_param=dict()
        for i,j in params.items():
            if i == 'act.os':
                enc_param[i] = j
            else:
                enc_param[i] = des_res(key,str(j))
        return enc_param

    def generate_params(self):
        data = self.get_register_data()
        key = data["k"]
        img_urls = [data['bg'], data['fg']]
        self.save_img(img_urls)
        rid = data['rid']
        organization = self.get_organization()
        ostype = 'web'
        callback = 'sm_1610006760346'
        sdkver = '1.1.3'
        rversion = '1.0.3'
        protocol = '66'
        params = self.get_ver_params(img_urls)
        params = self.enc_params(key,params)

        params.update({
            'rid': rid,
            'organization': organization,
            'ostype': ostype,
            'callback': callback,
            'sdkver': sdkver,
            'rversion': rversion,
            'protocol': protocol,
        })
        print(f"params:{params}")
        return params

    def get_index(self):
        params = self.generate_params()
        res = requests.get(self.fverify_url, headers=self.header, params=params)
        print(res.text)


if __name__ == '__main__':
    shumei = ShuMei()
    shumei.get_index()