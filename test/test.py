# -*- coding:utf-8 -*-
"""
@desc: 
"""
import time
from validate import Geetest

geetest = Geetest()
resp = geetest.validate("7e4fe1f3a3ebfec6e4af84f8090cdbbe", "127.0.0.1")

data = {
    "challenge": resp['second_challenge'],
    "hcash": "",
    "loginName": "19920120000",
    "venus": ""
}
resp = geetest.session.post('https://www.okex.com/v3/users/pwd/reset/first?t={}'.format(int(time.time() * 1000)), json=data, proxies={
    "http":"http://127.0.0.1:35124",
    "https":"http://127.0.0.1:35124",
}).json()
print(resp)