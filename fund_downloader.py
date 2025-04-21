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
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7,en-GB;q=0.6,ja;q=0.5",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "qgqp_b_id=5b9d8b5e63f579f82a73d131754bcbbb; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; st_si=38614788525230; st_asi=delete; ap_1_68c1f65b=1; EMFUND9=04-21 22:23:54@#$%u5929%u5F18%u4E2D%u8BC11000%u6307%u6570%u589E%u5F3AA@%23%24014201; st_pvi=34726450000364; st_sp=2023-04-16%2020%3A01%3A45; st_inirUrl=http%3A%2F%2Ffund.eastmoney.com%2Fdata%2Ffundranking.html; st_sn=3; st_psi=20250421222433451-112200305283-5103318229",
    "DNT": "1",
    "Host": "api.fund.eastmoney.com",
    "If-None-Match": "b56a685e-f638-4ccc-820d-c0495e577277",
    "Referer": "https://fundf10.eastmoney.com/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
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
    base_url = "https://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18306032015181749648_1745245483946&fundCode=%s&pageIndex=%d&pageSize=20&startDate=&endDate=&_=1745245484077"
    total_count = 0
    data = []  # sort by time inc

    def __init__(self, fund_code: str):
        self.func_code = fund_code

        self._download_data()

    def _download_data(self):
        total_count, page_size, first_page_data_list = self._download_page_data(1)

        self.total_count = total_count
        max_index = total_count
        self.data = [FundDailyInfo("", 0, 0.0) for x in range(max_index)]

        max_page = (total_count + page_size - 1) // page_size

        data_list = first_page_data_list
        for page in range(2, max_page + 1):
            _, _, page_data_list = self._download_page_data(page, max_page)

            data_list.extend(page_data_list)

        for idx, item in enumerate(data_list):
            index = max_index - idx - 1
            if item["JZZZL"] == "":
                item["JZZZL"] = "0.0"
            if item["DWJZ"] == "":
                item["DWJZ"] = "1.0"
            self.data[index] = FundDailyInfo(item["FSRQ"], float(item["DWJZ"]), float(item["JZZZL"]))


        print("\r", end="")

    def _download_page_data(self, page: int, max_page=-1):
        print(f"\rdownloading page {page}/{max_page}", end="")

        res = None
        for attempt in range(20):
            page_url = self.base_url % (self.func_code, page)
            try:
                res = requests.get(page_url, headers=headers)
            except Exception as e:
                print("error during requests.get({}), attempt={}, e={}".format(page_url, attempt, e))
            else:
                break

        left_index = res.text.find("(")
        right_index = res.text.rfind(")")
        data = json.loads(res.text[left_index + 1:right_index])

        total_count = data["TotalCount"]
        page_size = data["PageSize"]
        data_list = data["Data"]["LSJZList"]

        return total_count, page_size, data_list

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
