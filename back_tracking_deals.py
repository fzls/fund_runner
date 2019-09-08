#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# File   : back_tracking_deals
# Date   : 2019/9/1 0001
# Author : Chen Ji
# Email  : fzls.zju@gmail.com
# -------------------------------
import datetime

from fund_downloader import FundDownloader
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

    def run(self, start_time: str, end_time: str, ouput_file):
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

        last_info = None

        for info in self.fund.data:
            if self.in_range(info.time, start_time, end_time):
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
                    days = (datetime.datetime.now() - datetime.datetime.strptime(start_time, "%Y-%m-%d")).days
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
            res = profits[-1]
            duration = (datetime.datetime.strptime(end_time, "%Y-%m-%d") - datetime.datetime.strptime(start_time, "%Y-%m-%d")).days
            line = "%s,%s天,%s,%s,%s,%s,%s" % (
                self.fund_name, duration, self.strategy.name(), res["invest_money"], res["profit"], res["profit_rate"],
                res["annualized_profit_rate"])
            print(line)
            if ouput_file is not None:
                print(line, file=ouput_file)
        pass


if __name__ == '__main__':
    funds = [
        # 股票基金
        {"code": "110022", "name": "易方达消费行业股票"},

        # 债券基金
        {"code": "160621", "name": "鹏华丰和债券(LOF)A"},
        {"code": "470018", "name": "汇添富双利债券A"},
        {"code": "470018", "name": "汇添富双利债券A"},

        # 混合基金
        {"code": "519727", "name": "交银成长30混合"},
        {"code": "519778", "name": "交银经济新动力混合"},
        {"code": "673060", "name": "西部利得景瑞灵活配置混合"},

        # 大盘指数基金
        {"code": "070039", "name": "嘉实中证500ETF联接C"},
        {"code": "002987", "name": "广发沪深300ETF联接C"},

        # 行业指数基金
        {"code": "161725", "name": "招商中证白酒指数分级"},
        {"code": "160632", "name": "鹏华酒分级"},
        {"code": "160222", "name": "国泰国证食品饮料行业指数分级"},
    ]

    peroids = [
        7,
        14,
        30,
    ]

    times = [
        {"start": "2017-01-01", "end":"2018-01-01"},
        {"start": "2018-01-01", "end":"2019-01-01"},
        {"start": "2019-01-01", "end":"2020-01-01"},
        {"start": "2018-01-01", "end": "2020-01-01"},
    ]

    for t in times:
        start = t["start"]
        end = t["end"]
        with open("%s_%s.csv"%(start, end), "w+") as ouput_file:
            print("名称,时长,定投周期,总投入,总盈利,总盈利率,年化利率", file=ouput_file)
            for fund in funds:
                for peroid in peroids:
                    BackTrackingDeal(fund["code"], fund["name"], DingtouStrategy(days=peroid)).run(start, end, ouput_file)
