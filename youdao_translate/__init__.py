"""translation module.
Synopsis: fy word
"""
import os
import json
import urllib.parse
import hashlib
import requests
import random

from time import sleep
from albert import *

md_iid = "1.0"
md_version = "1.3"
md_id = "youdao_trans"
md_name = "Youdao Translate"
md_description = "Translate sentences using youdao_api"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/"
md_lib_dependencies = "requests"
md_maintainers = "@Fr13ndSDP"

TO_LANG = "zh"

class YouDaoAPI:
    ua = (
        "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/62.0.3202.62 Safari/537.36"
    )
    urltmpl = (
        "http://openapi.youdao.com/api"
        "?appKey={}"
        "&q={}&from=auto&to={}"
        "&salt={}&sign={}"
    )

    def __init__(self, word):
        self.word = word

    def get_url(self, src, dst, txt):
        # PRIVATE HERE
        appKey = #APPKEY
        secretKey = #TOKEN
        # salt is a six-digits random number
        salt = ""
        for i in range(6):
            ch = chr(random.randrange(ord("0"), ord("9") + 1))
            salt += ch
        sign = appKey + txt + salt + secretKey
        m1 = hashlib.md5()
        m1.update(sign.encode(encoding="utf-8"))
        sign = m1.hexdigest()
        q = urllib.parse.quote_plus(txt)
        url = self.urltmpl.format(appKey, q, dst, salt, sign)
        return url

    def get_result_from_api_as_dict(self):
        url = self.get_url("auto", TO_LANG, self.word)
        req = requests.get(url, headers={"User-Agent": self.ua})
        return json.loads(req.text)

    # Filter of dict content, return a new dict
    def generate_display(self):
        i = 1
        results = {}
        data = self.get_result_from_api_as_dict()

        if not data["isWord"]:
            if "translation" in data:
                for trans in data["translation"]:
                    results["translation "+ str(i)] = trans
                    i += 1
            else:
                results["Error"] = "Can not translate"

        else:
            i = 1
            if "basic" in data:
                if "phonetic" in data["basic"]:
                    results["phonetic"] = data["basic"]["phonetic"]
                if "explains" in data["basic"]:
                    for explain in data["basic"]["explains"]:
                        results["Dict: " + str(i)] = explain
                        i += 1
            else:
                results["Error"] = "Not in dictionary, try web"

            if "web" in data:
                for item in data["web"]:
                    results["Web: " + item["key"]] = ",".join(item["value"])

        return results

class Plugin(TriggerQueryHandler):
    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "fy "

    def synopsis(self):
        return "text"

    def initialize(self):
        self.icon = [os.path.dirname(__file__) + "/google_translate.png"]

    def handleTriggerQuery(self, query):
        results = []
        stripped = query.string.strip()
        if stripped:
            for number in range(30):
                sleep(0.01)
                if not query.isValid:
                    return

            translation = YouDaoAPI(stripped).generate_display()

            for key, val in translation.items():
                item = Item()
                item.icon = self.icon
                item.subtext = key
                item.text = val
                item.actions = [
                    Action(
                        "copy",
                        "Copy result to clipboard",
                        lambda t=item.text: setClipboardText(t),
                    )
                ]
                results.append(item)

            query.add(results)
        else:
            query.add(
                Item(
                    id=md_id,
                    text=md_name,
                    icon=self.icon,
                    subtext="Enter text to translate",
                )
            )
