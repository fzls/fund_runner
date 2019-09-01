#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# File   : strategy_inteface
# Date   : 2019/9/1 0001
# Author : Chen Ji
# Email  : fzls.zju@gmail.com
# -------------------------------
from abc import ABCMeta, abstractmethod


class StrategyInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    # 返回决策的基金份额或基金额度（正数，即买入时表示买入金额，负数，即卖出时则表示卖出份额）
    def run(self, time:str, net_values: list, profits: list, decision_shares: list, current_share: float,
            current_invest_money: float, sell_money: float) -> float:
        """

        :param time: str
        :param net_values: [FundDailyInfo]
        :param profits: [{time,invest_money, profit, profit_rate}]
        :param decision_shares: [float]
        :param current_share: float
        :param current_invest_money: float
        :param sell_money: float
        """
        pass
