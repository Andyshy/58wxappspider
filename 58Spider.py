# -*- coding:utf-8 -*-
import requests
from db import Mysql
PROXY_POOL_URL = 'http://127.0.0.1:5000/random'

"""整租"""


class Spider(object):
    def __init__(self):
        self.next_page = 27
        self.mysql = Mysql()

    def get_params(self, page):
        url = "https://wxapp.58.com/list/info"
        data = 'param={"cityId":102,"cateCode":"1","cateId":"8","dispCateId":"8","dispLocalId":102,"pageNum":%s,"key":"","queryList":{},"thirdKey":"%s"}&thirdKey=%s&appCode=0'
        thirdkey = "AmmkEZw03MCZg4oxLNghsH4qkQM3tVjRd4AyiRe9Lva5CzZllAIVR3YANNqj0w0m"
        data = data % (page, thirdkey, thirdkey)
        headers = {
            "charset": "utf-8",
            "Accept-Encoding": "gzip",
            "appcode": "0",
            "catecode": "",
            "scene": "1089",
            "Content-Length": "379",
            "Connection": "Keep-Alive",
            "content-type": "application/x-www-form-urlencoded,application/json",
            "thirdkey": "AmmkEZw03MCZg4oxLNghsH4qkQM3tVjRd4AyiRe9Lva5CzZllAIVR3YANNqj0w0m",
            "user-agent": "Mozilla/5.0 (Linux; Android 7.0; PRA-AL00 Build/HONORPRA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.143 Crosswalk/24.53.595.0 XWEB/257 MMWEBSDK/21 Mobile Safari/537.36 MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_CN MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_CN",
            "Host": "wxapp.58.com"
        }
        return data, headers

    def get_content(self, next_page, proxy):
        proxies = {
            "http":"http://"+ proxy,
            "https":"https://"+proxy
        }
        url = "https://wxapp.58.com/list/info"
        data, headers = self.get_params(next_page)
        try:
            r = requests.post(url, data=data, headers=headers, proxies=proxies)
        except requests.ConnectionError as e:
            print("请求失败", e)
            return False
        except r.status_code != 200 as e:
            print("请求失败", e)
        else:
            results = r.json()
            return results

    def parse_content(self, results):
        items = results.get("data").get("rstList")
        for item in items:
            yield{
                "infoId": str(item.get("infoId", "无")),
                "userId": str(item.get("userId", "无")),
                "dispCateName": item.get("dispCateName", "无"),
                "dispLocalName": item.get("dispLocalName", "无"),
                "title": item.get("title", "无"),
                "briefList": ",".join(item.get("briefList", "无")),
                "brief1":",".join(item.get("brief1", "无")),
                "price": item.get("price", "无"),
                "priceUnit": item.get("priceUnit", "无"),
                "postDate": item.get("postDate", "无")
            }

    def get_proxy(self):
        """得到一个代理，需要配合代理池的api参数"""
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                return response.text
            return False
        except requests.ConnectionError:
            return False

    def schedule(self):
        print("启动爬虫")
        while self.next_page:
            proxy = self.get_proxy()
            if proxy:
                results = self.get_content(self.next_page, proxy)
                if results:
                    for item in self.parse_content(results):
                        print(item)
                        self.mysql.insert(item)
                    next_page_condition = results.get("data").get("hasMore")
                    if next_page_condition == True:
                        self.next_page +=1
                    else:
                        print("请求完毕，本次请求成功{0}页面".format(self.next_page))
                        print("退出爬虫")
                        self.next_page = False
                        break
                else:
                    print("请求失败")
            else:
                print("获取代理失败")

if __name__ == "__main__":
    s = Spider()
    s.schedule()