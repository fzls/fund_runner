#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# File   : strategy_dingtou
# Date   : 2019/9/1 0001
# Author : Chen Ji
# Email  : fzls.zju@gmail.com
# -------------------------------
import datetime

from strategy_inteface import StrategyInterface


class DingtouStrategy(StrategyInterface):
    def run(self, time: str, net_values: list, profits: list, decision_shares: list, current_share: float,
            current_invest_money: float, sell_money: float) -> float:
        # 最简单的每周定投
        t = datetime.datetime.strptime(time, "%Y-%m-%d")
        if t.isoweekday() == 4:  # 每周四定投100
            return 100.0

        return 0.0
