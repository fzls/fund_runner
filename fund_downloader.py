#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# File   : fund_downloader.py
# Date   : 2019/9/1 0001
# Author : Chen Ji
# Email  : fzls.zju@gmail.com
# -------------------------------

import json
import os
import random
import shutil

import requests

# 若过期，则参考 https://fundf10.eastmoney.com/jjjz_000216.html 页面的请求，更新cookie
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7,en-GB;q=0.6,ja;q=0.5",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "qgqp_b_id=2678f31d9266f2a387bfd72a2eb6ae0d; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; HAList=ty-100-N225-%u65E5%u7ECF225; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND0=null; EMFUND8=02-05%2019%3A36%3A48@%23%24%u534E%u5B89%u65E5%u7ECF225ETF@%23%24513880; EMFUND9=02-05%2019%3A37%3A07@%23%24%u6613%u65B9%u8FBE%u65E5%u7ECF225ETF@%23%24513000; st_si=92844999740212; st_asi=delete; EMFUND7=02-11 16:11:28@#$%u534E%u5B89%u9EC4%u91D1%u6613ETF%u8054%u63A5A@%23%24000216; st_pvi=34726450000364; st_sp=2023-04-16%2020%3A01%3A45; st_inirUrl=http%3A%2F%2Ffund.eastmoney.com%2Fdata%2Ffundranking.html; st_sn=7; st_psi=20240211161221905-112200305283-7518348517",
    "DNT": "1",
    "Host": "api.fund.eastmoney.com",
    "If-None-Match": "b56a685e-f638-4ccc-820d-c0495e577277",
    "Referer": "https://fundf10.eastmoney.com/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
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
    data = []  # sort by time inc

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

    def __init__(self, code: str, name: str):
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


class FundGuzhiChartDownloader:
    get_all_funds_guzhi_api = "http://j4.dfcfw.com/charts/pic6/{code}.png?v={rand}"

    funds = []

    def __init__(self, code, name, result_dir):
        self.code = code
        self.name = name
        self.url = self.get_all_funds_guzhi_api.format(code=self.code, rand=random.random())
        self.result_dir = result_dir
        self.filepath = os.path.join(self.result_dir, '{}.png'.format(self.code))

    def save_to_local(self) -> bool:
        res = requests.get(self.url, stream=True)
        if res.status_code == 200:
            with open(self.filepath, 'wb') as f:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, f)

        return res.status_code == 200


if __name__ == '__main__':
    fd = FundGuzhiChartDownloader("161035", "富国中证医药主题指数增强", "guzhi_images")
    fd.save_to_local()
