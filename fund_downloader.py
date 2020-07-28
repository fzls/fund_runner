#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# File   : fund_downloader.py
# Date   : 2019/9/1 0001
# Author : Chen Ji
# Email  : fzls.zju@gmail.com
# -------------------------------

import json

import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7,en-GB;q=0.6,ja;q=0.5",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "ASP.NET_SessionId=ifqhxwf1tuwcui1rh4o2evdm; st_si=68354466271833; st_asi=delete; _adsame_fullscreen_16928=1; FundWebTradeUserInfo=JTdCJTIyQ3VzdG9tZXJObyUyMjolMjIlMjIsJTIyQ3VzdG9tZXJOYW1lJTIyOiUyMiUyMiwlMjJWaXBMZXZlbCUyMjolMjIlMjIsJTIyTFRva2VuJTIyOiUyMiUyMiwlMjJJc1Zpc2l0b3IlMjI6JTIyJTIyLCUyMlJpc2slMjI6JTIyJTIyJTdE; qgqp_b_id=30d909200d3019b496a281498c587c9a; _adsame_fullscreen_18503=1; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND0=null; EMFUND8=07-27%2016%3A36%3A00@%23%24%u4FE1%u8FBE%u6FB3%u94F6%u65B0%u80FD%u6E90%u4EA7%u4E1A%u80A1%u7968@%23%24001410; EMFUND9=07-27 16:36:11@#$%u56FD%u6CF0%u56FD%u8BC1%u6709%u8272%u91D1%u5C5E%u884C%u4E1A%u5206%u7EA7B@%23%24150197; st_pvi=55245435666572; st_sp=2019-04-01%2011%3A39%3A25; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=20; st_psi=20200727163640224-0-2607014817",
    "DNT": "1",
    "Host": "fund.eastmoney.com",
    "If-None-Match": "b56a685e-f638-4ccc-820d-c0495e577277",
    "Referer": "http://fund.eastmoney.com/data/fundranking.html",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
}


class FundDailyInfo:
    time = ""  # 日期
    unit_net_value = 0.0  # 单位净值
    daily_growth_rate = 0.0  # 日增长率

    def __init__(self, time: str, unit_net_val: float, daily_growth_rate: float):
        self.time = time
        self.unit_net_value = unit_net_val
        self.daily_growth_rate = daily_growth_rate

    def __str__(self):
        return "%s %f %f" % (self.time, self.unit_net_value, self.daily_growth_rate)


class FundDownloader:
    url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18304544093691286102_1567163891868&fundCode=%s&pageIndex=1&pageSize=%d&startDate=&endDate=&_=1567164070044"
    total_count = 0
    data = [] # sort by time inc

    def __init__(self, fund_code: str, page_size=10000):
        self.url = self.url % (fund_code, page_size)
        self._download_data()

    def _download_data(self):
        res = None
        for attempt in range(20):
            try:
                res = requests.get(self.url, headers=headers)
            except Exception as e:
                print("error during requests.get({}), attempt={}, e={}".format(self.url, attempt, e))
            else:
                break

        left_index = res.text.find("(")
        right_index = res.text.rfind(")")
        data = json.loads(res.text[left_index + 1:right_index])

        self.total_count = data["TotalCount"]
        max_index = min(data["TotalCount"], data["PageSize"])
        self.data = [FundDailyInfo("", 0, 0.0) for x in range(max_index)]
        for idx, item in enumerate(data["Data"]["LSJZList"]):
            index = max_index - idx - 1
            if item["JZZZL"] == "":
                item["JZZZL"] = "0.0"
            if item["DWJZ"] == "":
                item["DWJZ"] = "1.0"
            self.data[index] = FundDailyInfo(item["FSRQ"], float(item["DWJZ"]), float(item["JZZZL"]))

    def print(self):
        for info in self.data:
            print(info)

class FundInfo:
    code = ""
    name = ""

    def __init__(self, code:str, name:str):
        self.code = code
        self.name = name

    def __str__(self):
        return "%s %s" % (self.code, self.name)

class AllFundDownloader:
    get_all_funds_api = "http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=zzf&st=desc&sd=2019-01-06&ed=2020-01-06&qdii=&tabSubtype=,,,,,&pi=1&pn=60000&dx=1&v=0.5921715210640965"

    funds = []

    def __init__(self):
        res = requests.get(self.get_all_funds_api, headers=headers)
        left = "datas:"
        right = ",allRecords"
        left_index = res.text.find(left)
        right_index = res.text.rfind(right)
        data = json.loads(res.text[left_index + len(left):right_index])

        for str in data:
            cols = str.split(",")
            code = cols[0]
            name = cols[1]
            self.funds.append(FundInfo(code, name))

    def print(self):
        for info in self.funds:
            print(info)


if __name__ == '__main__':
    fd = AllFundDownloader()
    fd.print()