#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# File   : back_tracking_deals
# Date   : 2019/9/1 0001
# Author : Chen Ji
# Email  : fzls.zju@gmail.com
# -------------------------------
import datetime
import os
import pathlib
import shutil
import webbrowser

import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.pylab import datestr2num

from fund_downloader import FundDownloader, AllFundDownloader, FundGuzhiChartDownloader
from strategy_dingtou import DingtouStrategy
from strategy_inteface import StrategyInterface


class BackTrackingDeal:
    fund_code = ""  # 基金代码
    fund_name = ""  # 基金名称

    strategy = StrategyInterface()  # 策略

    # fund: type FundDownloader

    def __init__(self, func_code: str, fund_name: str, strategy: StrategyInterface):
        self.fund_code = func_code
        self.fund_name = fund_name
        self.fund = FundDownloader(func_code)

        self.strategy = strategy

    def in_range(self, time: str, start: str, end: str) -> bool:
        return datetime.datetime.strptime(start, "%Y-%m-%d") <= \
            datetime.datetime.strptime(time, "%Y-%m-%d") <= \
            datetime.datetime.strptime(end, "%Y-%m-%d")

    def get_data_index(self, time: str) -> int:
        target = datetime.datetime.strptime(time, "%Y-%m-%d")
        if target <= datetime.datetime.strptime(self.fund.data[0].time, "%Y-%m-%d"):
            return 0
        if target >= datetime.datetime.strptime(self.fund.data[-1].time, "%Y-%m-%d"):
            return len(self.fund.data) - 1

        low = 0
        high = len(self.fund.data) - 1
        while low <= high:
            i = (low + high) // 2
            t = datetime.datetime.strptime(self.fund.data[i].time, "%Y-%m-%d")
            if t == target:
                return i
            elif t < target:
                low = i + 1
            else:
                high = i - 1

        return low

    def get_range_data(self, start: str, end: str) -> list:
        return self.fund.data[self.get_data_index(start): self.get_data_index(end) + 1]

    def run(self, start_time: str, end_time: str) -> dict:
        """

        :param start_time: 开始时间，如2019-08-21
        :param end_time: 结束时间，如2019-08-30
        """
        # TODO：按照特定策略去跑该段时间的回测
        net_values = []  # FundDailyInfo
        profits = []  # float 当日收益情况
        decisions = []  # float 历史投资决策信息，负数表示卖出份额，0表示不动，正数表示买入金额
        invest_money = 0.0  # 总投资金额
        invest_share = 0.0  # 总投资份额
        sell_money = 0.0  # 总卖出金额

        first_info = None
        last_info = None

        for info in self.get_range_data(start_time, end_time):
            if first_info is None:
                first_info = info

            if last_info is not None:
                # 处理T-1日的决策信息
                net_values.append(last_info)
                # 更新总投资金额和份额，并更新收益情况
                decision = decisions[-1]
                if decision != 0.0:
                    decision_share = 0.0
                    if decision > 0.0:  # 买入金额
                        invest_money += decision
                        decision_share = decision / last_info.unit_net_value
                    if decision < 0.0:  # 卖出份额
                        sell_money += -decision * last_info.unit_net_value
                        decision_share = decision

                    invest_share += decision_share

                profit = invest_share * last_info.unit_net_value + sell_money - invest_money
                profit_rate = "0%"
                annualized_profit_rate = "0%"
                days = (datetime.datetime.strptime(end_time, "%Y-%m-%d") - datetime.datetime.strptime(start_time,
                                                                                                      "%Y-%m-%d")).days
                if invest_money != 0:
                    profit_rate = "%.4f%%" % (100 * profit / invest_money)
                    annualized_profit_rate = "%.4f%%" % (100 * profit / invest_money * 365 / days)

                profits.append({
                    "time": last_info.time,
                    "invest_money": invest_money,
                    "profit": profit,
                    "profit_rate": profit_rate,
                    "share": invest_share,
                    "share_money": invest_share * last_info.unit_net_value,
                    "sell_money": sell_money,
                    "annualized_profit_rate": annualized_profit_rate,
                    "unit_net_value_change_rate": "%.4f%%" % (100 * (last_info.unit_net_value - first_info.unit_net_value) / first_info.unit_net_value)
                })

            # T日
            # 根据策略做决策
            decision = self.strategy.run(info.time, net_values,
                                         profits,
                                         decisions,
                                         invest_share, invest_money, sell_money)

            # 添加决策
            decisions.append(decision)

            last_info = info
        if len(profits) != 0:
            return profits[-1]
        return {}
        pass


def get_dingtou_days():
    days = []
    start = datetime.datetime.strptime("2019-10-23", "%Y-%m-%d")
    now = datetime.datetime.now()
    while start < now:
        days.append(start.strftime("%Y-%m-%d"))
        if start.month < 12:
            start = start.replace(month=start.month + 1)
        else:
            start = start.replace(year=start.year + 1, month=1)

    return days


def merge_images_vertically_and_display(images_to_merge):
    images = [Image.open(x) for x in images_to_merge]
    widths, heights = zip(*(i.size for i in images))

    max_width = max(widths)
    total_height = sum(heights)

    new_im = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    merge_result_path = '今日合并估值.png'
    new_im.save(merge_result_path)
    print("合并所有今日估值图片到{}".format(merge_result_path))

    # 展现结果
    webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(merge_result_path)


# 选项开关
# MODE_SELECTED_ONLY = True
MODE_SELECTED_ONLY = False
if MODE_SELECTED_ONLY:
    DRAW_PLOTS = True
    USE_ALL_FUNDS = False
    FETCH_FUNDS_GUZHI = True
else:
    DRAW_PLOTS = False
    USE_ALL_FUNDS = True
    FETCH_FUNDS_GUZHI = False


def main():
    funds = [
        # # # 股票基金
        # {"code": "004851", "name": "广发医疗保健股票"},
        # {"code": "000913", "name": "农银医疗保健股票"},
        # {"code": "000960", "name": "招商医药健康产业股票"},
        #
        # # # 债券基金
        # {"code": "005461", "name": "南方希元转债"},
        # {"code": "000080", "name": "天治可转债增强债券A"},
        # {"code": "004993", "name": "中欧可转债债券A"},
        # #
        # # # 混合基金
        # {"code": "050026", "name": "博时医疗保健行业混合A"},
        # {"code": "003096", "name": "中欧医疗健康混合C"},
        # {"code": "005689", "name": "中银医疗保健混合"},
        # #
        # # # 大盘指数基金
        # {"code": "070039", "name": "嘉实中证500ETF联接C"},
        # {"code": "002987", "name": "广发沪深300ETF联接C"},
        #
        # # # 行业指数基金
        # {"code": "161035", "name": "富国中证医药主题指数增强"},
        # {"code": "161122", "name": "易方达生物分级"},
        # {"code": "161726", "name": "招商国证生物医药指数分级"},

        {"code": "005314", "name": "万家中证1000指数增强C"},
        {"code": "110035", "name": "易方达双债增强债券A"},
        {"code": "004011", "name": "华泰柏瑞鼎利C"},
        {"code": "009272", "name": "博时信用优选C"},
    ]

    if USE_ALL_FUNDS:
        print("拉取全部基金列表")
        funds = []
        allFunds = AllFundDownloader()
        for fund in allFunds.funds:
            funds.append({
                "code": fund.code,
                "name": fund.name,
            })

    # 下载每日净值图
    if FETCH_FUNDS_GUZHI:
        guzhi_images_dir = "guzhi_images"
        print("下载每日净值图到{}".format(guzhi_images_dir))
        # 创建结果目录
        shutil.rmtree(guzhi_images_dir, True)
        pathlib.Path(guzhi_images_dir).mkdir(parents=True, exist_ok=True)
        for idx, fund in enumerate(funds):
            chartDownloader = FundGuzhiChartDownloader(fund["code"], fund["name"], guzhi_images_dir)
            res = ""
            if chartDownloader.save_to_local():
                res = "成功"
            else:
                res = "失败"
            print("[{}/{}] 下载{}-{}成功, url={}".format(idx + 1, len(funds), chartDownloader.code, chartDownloader.name, chartDownloader.url))

        # 合并为一个图
        print("合并为单个图")
        images_to_merge = []
        for filename in os.listdir(guzhi_images_dir):
            filepath = os.path.join(guzhi_images_dir, filename)
            if filename.endswith(".png"):
                images_to_merge.append(filepath)

        merge_images_vertically_and_display(images_to_merge)

    peroids = [
        7,
        14,
        30,
    ]

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    lastMonth = (datetime.datetime.now() - datetime.timedelta(days=int(365 / 12 * 1))).strftime("%Y-%m-%d")
    lastTwoMonth = (datetime.datetime.now() - datetime.timedelta(days=int(365 / 12 * 2))).strftime("%Y-%m-%d")
    lastSeason = (datetime.datetime.now() - datetime.timedelta(days=int(365 / 12 * 3))).strftime("%Y-%m-%d")
    lastFourMonth = (datetime.datetime.now() - datetime.timedelta(days=int(365 / 12 * 4))).strftime("%Y-%m-%d")
    lastFiveMonth = (datetime.datetime.now() - datetime.timedelta(days=int(365 / 12 * 5))).strftime("%Y-%m-%d")
    lastHalfYear = (datetime.datetime.now() - datetime.timedelta(days=int(365 / 12 * 6))).strftime("%Y-%m-%d")
    lastYear = (datetime.datetime.now() - datetime.timedelta(days=int(365))).strftime("%Y-%m-%d")
    lastTwoYear = (datetime.datetime.now() - datetime.timedelta(days=int(365 * 2))).strftime("%Y-%m-%d")
    lastThreeYear = (datetime.datetime.now() - datetime.timedelta(days=int(365 * 3))).strftime("%Y-%m-%d")
    times = [
        {"start": lastMonth, "end": now},  # 上个月
        # {"start": lastTwoMonth, "end": now},  # 前两个月
        {"start": lastSeason, "end": now},  # 上个季度
        # {"start": lastFourMonth, "end": now},  # 前四个月
        # {"start": lastFiveMonth, "end": now},  # 前五个月
        {"start": lastHalfYear, "end": now},  # 前半年
        {"start": lastYear, "end": now},  # 前年
        {"start": lastTwoYear, "end": now},  # 前两年
        {"start": lastThreeYear, "end": now},  # 前三年
        {"start": lastThreeYear, "end": lastTwoYear},  # 前三年到前两年，方便回溯
        {"start": lastTwoYear, "end": lastYear},  # 前两年到去年，方便回溯
    ]

    fund_deal_map = {}
    for idx, fund in enumerate(funds):
        #  获取基金数据
        print("[%d/%d] Loading data for %s" % (idx + 1, len(funds), fund["name"]))
        fund_deal_map[fund["name"]] = BackTrackingDeal(fund["code"], fund["name"], DingtouStrategy(days=1))

    if DRAW_PLOTS:
        # 绘走势图
        # plt.style.use('ggplot')
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        # plt.title(u'基金走势图')
        fig, axs = plt.subplots(len(fund_deal_map), figsize=(10, 5 * len(fund_deal_map)))
        idx = 0
        start_dingtou_time = "2019-10-15"
        for name, fund in fund_deal_map.items():
            data = fund.get_range_data(start_dingtou_time, now)
            # data = fund.fund.data
            x = range(len(data))
            x_date = [datestr2num(i.time) for i in data]
            y_data = [i.unit_net_value for i in data]

            fund.strategy = DingtouStrategy(days=30)
            profit = fund.run(start_dingtou_time, now)

            total_change_rate = (data[-1].unit_net_value - data[0].unit_net_value) / data[0].unit_net_value * 100
            axs[idx].plot_date(x_date, y_data, '-', label=u"%s-%s-[%f%%]-[%s]" % (fund.fund_code, fund.fund_name, total_change_rate, profit["profit_rate"]))
            for day in get_dingtou_days():
                axs[idx].axvline(datestr2num(day), ymin=0.0, ymax=1.0, color="gray")
            axs[idx].legend()
            axs[idx].grid(True)
            idx += 1
        plt.xlabel(u'时间')
        plt.ylabel(u'单位净值')
        # plt.show()
        plt.savefig("profit.png")
        webbrowser.get("C:/Program Files/Google/Chrome/Application/chrome.exe %s").open(os.path.realpath("profit.png"))

    # 清空结果目录
    result_dir = "result"
    if os.path.isdir(result_dir):
        shutil.rmtree(result_dir)
    print("output directory cleared")

    for t in times:
        start = t["start"]
        end = t["end"]
        duration = (datetime.datetime.strptime(end, "%Y-%m-%d") - datetime.datetime.strptime(start, "%Y-%m-%d")).days
        file_name = f"{result_dir}/{start}_{end}.csv"
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        summary = {}
        for peroid in peroids:
            summary[peroid] = {
                "fund_name": "平均",
                "duration": duration,
                "strategy": "%d天" % peroid,
                "invest_money": 0.001,
                "profit": 0.0,
                "profit_rate": "0%",
                "annualized_profit_rate": "0%",
                "unit_net_value_change_rate": "",
            }

        outputs = []
        for fund in funds:
            fund_deal = fund_deal_map[fund["name"]]
            for peroid in peroids:
                # 尝试不同策略
                strategy = DingtouStrategy(days=peroid)
                fund_deal.strategy = strategy
                profit = fund_deal.run(start, end)
                if len(profit) != 0:
                    outputs.append({
                        "fund_name": fund["name"],
                        "duration": duration,
                        "strategy": strategy.name(),
                        "invest_money": profit["invest_money"],
                        "profit": profit["profit"],
                        "profit_rate": profit["profit_rate"],
                        "annualized_profit_rate": profit["annualized_profit_rate"],
                        "unit_net_value_change_rate": profit["unit_net_value_change_rate"],
                    })

                    # show status
                    line = "%s,%s天,%s,%s,%s,%s,%s,%s" % (
                        fund["name"],
                        duration,
                        strategy.name(),
                        profit["invest_money"],
                        profit["profit"],
                        profit["profit_rate"],
                        profit["annualized_profit_rate"],
                        profit["unit_net_value_change_rate"],
                    )
                    print(line)

                    summary[peroid]["invest_money"] += profit["invest_money"]
                    summary[peroid]["profit"] += profit["profit"]

        outputs.sort(key=lambda x: x["profit"], reverse=True)

        for k, v in summary.items():
            v["profit_rate"] = "%.4f%%" % (100 * v["profit"] / v["invest_money"])
            v["annualized_profit_rate"] = "%.4f%%" % (100 * v["profit"] / v["invest_money"] * 365 / duration)
            outputs.append(v)

        with open(file_name, "w+") as ouput_file:
            print("名称,时长,定投周期,总投入,总盈利,总盈利率,年化利率,净值变化率", file=ouput_file)

            for output in outputs:
                line = "%s,%s天,%s,%s,%s,%s,%s,%s" % (
                    output["fund_name"],
                    output["duration"],
                    output["strategy"],
                    output["invest_money"],
                    output["profit"],
                    output["profit_rate"],
                    output["annualized_profit_rate"],
                    output["unit_net_value_change_rate"],
                )
                print(line, file=ouput_file)


if __name__ == '__main__':
    main()
