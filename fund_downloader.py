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
    "Cookie": "qgqp_b_id=bb4ded2cbf6298d0f64987e0dbe18f38; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; st_si=00114758560421; st_asi=delete; EMFUND9=08-30 19:17:51@#$%u6613%u65B9%u8FBE%u6D88%u8D39%u884C%u4E1A%u80A1%u7968@%23%24110022; st_pvi=55245435666572; st_sp=2019-04-01%2011%3A39%3A25; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=6; st_psi=20190830191751422-0-5230010871",
    "DNT": "1",
    "Host": "api.fund.eastmoney.com",
    "If-None-Match": "b56a685e-f638-4ccc-820d-c0495e577277",
    "Referer": "http://fundf10.eastmoney.com/jjjz_110022.html",
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
        res = requests.get(self.url, headers=headers)
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
            self.data[index] = FundDailyInfo(item["FSRQ"], float(item["DWJZ"]), float(item["JZZZL"]))

    def print(self):
        for info in self.data:
            print(info)

if __name__ == '__main__':
    fd = FundDownloader("110022")
    fd.print()