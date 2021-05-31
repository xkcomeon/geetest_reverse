# -*- coding:utf-8 -*-
"""
@desc: 
"""
import os
import random
import logging
import re
import warnings
from urllib.parse import urljoin

import execjs
import requests

from utils import get_gap_position, get_standard_img, get_track, get_base_data

os.chdir(os.path.join(os.path.dirname(__file__), "js"))

warnings.filterwarnings(action="ignore")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('geetest')
logging.getLogger("urllib3").setLevel(logging.ERROR)


class Geetest:
    gt = "7e4fe1f3a3ebfec6e4af84f8090cdbbe" # okex
    # gt = "ad3086eed38c305af4d2add2132e771e" # 蛋壳
    get_php_response = {}
    debug = False # 手动输入轨迹值

    def __init__(self):
        self.session = self.get_session()
        self.ctx_sense = execjs.compile(self.read("sense.js"))
        self.ctx_slide = execjs.compile(self.read("slide_decoce.js"))

    def get_img_track(self, gt, proxy):
        base_data = get_base_data(gt, proxy)
        base_data = self.ctx_sense.call("stringify",base_data)
        self.key = self.ctx_sense.call("get_key")
        data = self.ctx_sense.call("encrypt", base_data, self.key['aeskey']) + self.key['rsa']
        response = self.session.post('https://api.geetest.com/gt_judgement?pt=0&gt={}'.format(gt),
                                     data=data).json()
        challenge = response['challenge']
        body = {"is_next": True, "type": "slide3", "gt": gt, "challenge": challenge,
                "lang": "zh-cn", "https": False, "protocol": "https://", "product": "embed", "width": "100%",
                "api_server": "api.geetest.com", "static_servers": ["static.geetest.com", "dn-staticdown.qbox.me"],
                "post": True}
        response = self.session.post('https://api.geetest.com/get.php', json=body).json()
        new_challenge = response['challenge']
        self.get_php_response = response
        bg_url = urljoin("https://static.geetest.com/", response['bg'])
        response = self.session.get(bg_url).content  # 图片
        standard_img = get_standard_img(response)
        gap_position = get_gap_position(standard_img)
        logger.debug("gap_position:{}".format(gap_position))
        self.ctx_gct = self.get_gct_ctx()
        if self.debug:
            standard_img.show()
        return challenge, new_challenge, gap_position

    def get_gct_ctx(self):
        gct = self.session.get(urljoin("https://static.geetest.com/", self.get_php_response['gct_path'])).text
        # 提取出js, 将gct关键代码抽离并替换近slide.js
        temp = re.sub(r'return (function\(t\)\{[\s\S]*?\});',
                      lambda x: "window._gct=" + x.group(1) + ";" + "return " + x.group(1), gct[12:-5])

        # res  = re.sub(r"decodeURI\('([\s\S]*?)'\);", lambda x:"decodeURI('" + x.group(1).replace("'", "\\'") + "');", temp)
        res2 = "window={};" + temp + "\n" + '''function get_gct(b){
    window._gct(b)
    return b;
}'''
        return execjs.compile(res2)

    def get_w(self, challenge, offset, track, gt):
        """
        w的获取过程
        是对temp.js中对象的加密得到的一个字符串
        生成w参数的所需要的json说明
            lang 固定值 zh-cn
            userresponse 缺口x轴位置和challenge加密所得, offset其实是你拖动的x轴距离
            passtime 拖动花费时间, 也是轨迹列表[-1][-1]的值
            imgload 图片加载时间 随机构造即可
            aa 是对拖动轨迹外加get.php返回的c,s加密所得
            eq 类似于各加载时间的记录，目测可以伪造
            t4qx 这个参数名可能会变 方法在window._gct

            rp get_rp(gt+challenge:前32位 + passtime)
        """
        passtime = track[-1][-1]
        aa = self.ctx_slide.call("get_aa", track, self.get_php_response['c'], self.get_php_response['s'])
        logger.debug('获取到参数aa:{}'.format(aa))
        userresponse = self.ctx_slide.call("getUserResponse", offset, challenge)
        logger.debug('获取到参数userresponse,offset:{},challenge:{},result:{}'.format(offset, challenge, userresponse))
        rp = self.ctx_slide.call("get_rp", gt + challenge[0:32] + str(passtime))
        logger.debug('获取到参数rp:{}'.format(rp))
        # 额外参数
        u = {
            "lang": "zh-cn",
            "userresponse": userresponse,
            "passtime": passtime,
            "imgload": random.randint(110, 180),
            "aa": aa,
            "ep": {
                "v": "7.8.0",
                "te": False,
                "me": True,
                "tm": {
                    "v": "7.8.1",
                    "te": False,
                    "me": True,
                    "tm": {
                        "a": 1622192118410,
                        "b": 1622192118756,
                        "c": 1622192118756,
                        "d": 0,
                        "e": 0,
                        "f": 1622192118414,
                        "g": 1622192118414,
                        "h": 1622192118414,
                        "i": 1622192118414,
                        "j": 1622192118414,
                        "k": 0,
                        "l": 1622192118418,
                        "m": 1622192118743,
                        "n": 1622192118809,
                        "o": 1622192118759,
                        "p": 1622192119281,
                        "q": 1622192119281,
                        "r": 1622192119284,
                        "s": 1622192120264,
                        "t": 1622192120264,
                        "u": 1622192120264
                    },
                    "td": -1
                },
                "td": -1
            },
            "rp": rp
        }

        extra = self.ctx_gct.call("get_gct", {"lang": "zh-cn", "ep": u['ep']})
        extra.pop("ep", None)
        extra.pop("lang", None)
        u.update(extra)
        logger.debug('获取到随机参数:{}'.format(extra))
        aeskey = self.ctx_slide.call("get_aeskey")
        rsa = self.ctx_slide.call("get_rsa", aeskey)
        logger.debug('获取w末尾填充值:{}'.format(rsa))
        w = self.ctx_sense.call("encrypt_w", u, aeskey) + rsa
        logger.debug("获取轨迹加密值w:{},,,,加密key:{}".format(w, aeskey))

        return w

    def validate(self, gt, ip):
        # challenge 缺口位置
        challenge, new_challenge, gap_position = self.get_img_track(gt, ip)
        if self.debug:
            track = eval(input("请输入track值\n"))
        else:
            track = get_track(offset=gap_position[0])
        w = self.get_w(new_challenge, track[-1][0] - 1, track, gt)
        data = {
            "challenge": challenge,
            "client_type": "web",
            "gt": gt,
            "lang": "zh-cn",
            "pt": 0,
            "w": w
        }

        resp = self.session.post("https://api.geetest.com/ajax.php", json=data).json()
        if resp.get("validate"):
            return {
                "challenge":challenge,
                "second_challenge":new_challenge,
                "validate":resp['validate']
            }
        else:
            raise Exception("验证失败")

    @staticmethod
    def get_session():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",

        }
        session = requests.session()
        session.headers = headers
        session.verify = False
        session.proxies = {
            # "https":"http://127.0.0.1:35124",
            # "http":"http://127.0.0.1:35124",
        }
        return session

    @staticmethod
    def read(path):
        path = os.path.join(os.path.join(os.path.dirname(__file__), "js"), path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content


