#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# File   : back_tracking_deals
# Date   : 2019/9/1 0001
# Author : Chen Ji
# Email  : fzls.zju@gmail.com
# -------------------------------
import datetime
import pprint

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

    def run(self, start_time: str, end_time: str):
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
                    profit_rate = 0.0
                    if invest_money != 0:
                        profit_rate = profit / invest_money

                    profits.append({
                        "time": last_info.time,
                        "invest_money": invest_money,
                        "profit": profit,
                        "profit_rate": profit_rate,
                        "share": invest_share,
                        "share_money": invest_share * last_info.unit_net_value,
                        "sell_money": sell_money,
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

        pprint.pprint(profits, indent=2)
        pass


if __name__ == '__main__':
    btd = BackTrackingDeal("110022", "易方达消费行业股票", DingtouStrategy())
    # btd.run("2019-01-01", "2019-08-31")
    btd.run("2019-01-01", "2019-08-31")
