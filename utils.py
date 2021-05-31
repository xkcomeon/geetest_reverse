# -*- coding:utf-8 -*-
"""
@desc: 
"""
import re
import json
import telnetlib
import os
from io import BytesIO

from PIL import Image
import numpy as np

position = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12,
            13, 23, 22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]

tracks_path = os.path.join(os.path.dirname(__file__), "tracks.json")
with open(tracks_path, "r") as f:
    tracks = json.load(f)


def get_base_data(gt=None, proxy=None):
    base_data = {
        "id": gt,
        "page_id": 1622194416904,
        "lang": "zh-cn",
        "platform": "PC",
        "data": {
            "insights": "30736!!191554!!CSS1Compat!!139!!-1!!-1!!-1!!-1!!2!!-1!!-1!!-1!!4!!1!!-1!!24!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!123!!2!!-1!!-1!!-1!!-1478!!121!!-1536!!5!!411!!708!!1351!!828!!zh-CN!!zh-CN,zh!!-1!!1.25!!24!!Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36!!1!!1!!1536!!865!!1536!!825!!1!!1!!1!!-1!!Win32!!0!!-8!!ec7c335bf74657c936dd67ab696b3d97!!f2d2e0dd416d822848daae7931504cd5!!internal-pdf-viewer,mhjfbmdgcfjbbpaeojofohoefgiehjai,internal-nacl-plugin!!0!!-1!!0!!16!!Arial,ArialBlack,ArialNarrow,BookAntiqua,BookmanOldStyle,Calibri,Cambria,CambriaMath,Century,CenturyGothic,CenturySchoolbook,ComicSansMS,Consolas,Courier,CourierNew,Garamond,Georgia,Helvetica,Impact,LucidaBright,LucidaCalligraphy,LucidaConsole,LucidaFax,LucidaHandwriting,LucidaSans,LucidaSansTypewriter,LucidaSansUnicode,MicrosoftSansSerif,MonotypeCorsiva,MSGothic,MSPGothic,MSReferenceSansSerif,MSSansSerif,MSSerif,PalatinoLinotype,SegoePrint,SegoeScript,SegoeUI,SegoeUILight,SegoeUISemibold,SegoeUISymbol,Tahoma,Times,TimesNewRoman,TrebuchetMS,Verdana,Wingdings,Wingdings2,Wingdings3!!1622194418478!!-1!!-1!!-1!!173!!18!!8!!81!!30!!-1!!-1",
            "track": "M.O8PjIA38Pj5A3(?(((f5,(b,(:M((((((:(e-9A9K2NjG**).hMjOCK)O2K1-0RjS)O/K,1T-:p/S0S0OJRkNlgj-1-/OE-1K)*7-2.kkh?)EU(iPI5,(nbe(,e(8(8bq5cSWb9YFb9hlb9NH8*(N(n-)bE1n-*9n/*0)(P-M/)M5-)4)(9-MbM/)()(9b9/)(5/)(E-(bE/)()M9(E-(Lqqqj(l9(5(85b(((,,,qbb5(nec/P1K*)RYg7))E--K)(gM96@Bf6,1c9j-)1E-(-j1*M97)(E-*Mb-MM9-N3)(@)(M93)(?MU(((((((",
            "ep": {
                "ts": 1622194418481,
                "v": "1.3.9",
                "f": "406ec650",
                "em": {
                    "ph": 0,
                    "cp": 0,
                    "ek": "11",
                    "wd": 1,
                    "nt": 0,
                    "si": 0,
                    "sc": 0
                },
                "te": False,
                "me": True,
                "tm": {
                    "a": 1622194415632,
                    "b": 1622194416058,
                    "c": 1622194416058,
                    "d": 0,
                    "e": 0,
                    "f": 1622194415634,
                    "g": 1622194415634,
                    "h": 1622194415634,
                    "i": 1622194415634,
                    "j": 1622194415634,
                    "k": 0,
                    "l": 1622194415636,
                    "m": 1622194416044,
                    "n": 1622194416203,
                    "o": 1622194416061,
                    "p": 1622194416456,
                    "q": 1622194416456,
                    "r": 1622194416460,
                    "s": 1622194416903,
                    "t": 1622194416903,
                    "u": 1622194416903
                },
                "action": "client",
                "ip": "{},0.0.0.0".format(proxy)
            },
            "eco": "a3ad9f87f726554ddeb58b5a3c42140b",
            "ww3": -1
        },
        "interactive": 1
    }
    return base_data


def get_standard_img(content):
    image = Image.open(BytesIO(content))
    standard_img = Image.new("RGBA", (260, 160))
    s, u = 80, 10
    for c in range(52):
        a = position[c] % 26 * 12 + 1
        b = s if position[c] > 25 else 0
        im = image.crop(box=(a, b, a + 10, b + 80))
        standard_img.paste(im, box=(c % 26 * 10, 80 if c > 25 else 0))
    return standard_img


def get_gap_position(image):
    """横向连续40个像素点像素值小于100，100，100"""
    array = np.delete(np.array(image), -1, 2)
    height, width, _ = array.shape
    for threshold in range(40, 120, 10):
        for y in range(height - 40):
            for x in range(60, width - 40):
                if np.all(array[y:y + 1][x:x + 15] < threshold) and np.all(array[y:y + 15, x:x + 1] < threshold):
                    return x, y
    return False


def get_unicode_encode(base: str):
    res = ''
    for i in base:
        res += ("\\u" + hex(ord(i))[2:].rjust(4, "0"))
    return res


def replace(x):
    res = '\\u{}'.format(x.group(1)[-4:]).encode('utf-8').decode('unicode_escape')
    if re.match("^[A-Za-z0-9_-]*$", res) and not res.isspace():
        return res
    else:
        return x.group(1)


def decode_js(content):
    """解码类似\u0036的字符,便于读懂"""
    content = re.sub(r'(\\u[a-f0-9]{4})', lambda x: replace(x), content)
    return content


def get_track(offset):
    for track in tracks:
        if offset == track[-1][0]:
            return track


def validate_proxy(ip, port):
    try:
        telnetlib.Telnet(ip, port, timeout=2)
        return True
    except:
        return False

def stringify(data:dict):
    res = ''
    for key, value in data.items():
        if isinstance(value, dict):
            res += '%s:%s,' % (key, stringify(value))
        else:
            res += '{}:{},'.format(key, json.dumps(value))

    return '{' + res.rstrip(",") +  '}'

