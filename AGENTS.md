# AGENTS.md

## 项目概述

基金定投回测工具。从东方财富 API 拉取基金历史净值数据，用多种定投策略进行回测，输出 CSV 报表和收益折线图。

## 环境搭建

```bash
# 首次：创建 venv 并安装依赖
python -m venv .venv_dev
call .venv_dev\Scripts\activate.bat   # Windows
pip install -i https://pypi.doubanio.com/simple -r requirements.txt
```

依赖仅两个：`matplotlib==3.3.0`、`requests==2.24.0`。

## 运行

```bash
python back_tracking_deals.py
```

唯一的入口文件。运行后会：
1. 从东方财富 API 下载基金净值数据（首次慢，后续从 `.fund_cache/` 读取，缓存 6 小时过期）
2. 对 `main()` 中 `funds` 列表里的基金跑多个定投周期（7/14/30 天）的回测
3. 结果输出到 `result/` 目录的 CSV 文件，图表保存为 `profit.png` 并用 Chrome 打开

## 文件结构

| 文件 | 职责 |
|---|---|
| `back_tracking_deals.py` | **主入口**。包含回测引擎 `BackTrackingDeal`、图表生成、`main()` |
| `fund_downloader.py` | 从东方财富 API 拉取基金净值，带文件缓存（`.fund_cache/`） |
| `strategy_inteface.py` | 策略抽象基类 `StrategyInterface` |
| `strategy_dingtou.py` | 定投策略实现 `DingtouStrategy` |
| `_init_and_activate_venv.bat` | 首次环境初始化脚本 |
| `_install_requirements.bat` | 仅安装依赖（复用已有 venv） |

## 关键约束

- **平台**：仅 Windows。代码中有硬编码的 Chrome 路径（`C:/Program Files/Google/Chrome/Application/chrome.exe`）和 `.bat` 脚本。
- **API Cookie 过期**：`fund_downloader.py:22-35` 的 `headers` 包含硬编码的 Cookie，过期后请求会失败。需参考 `https://fundf10.eastmoney.com/jjjz_000216.html` 页面的请求更新 Cookie。
- **无测试、无 lint、无 CI**：整个项目没有测试套件、类型检查或代码风格工具。修改时需手动验证。
- **基金列表硬编码**：`back_tracking_deals.py:205-265` 的 `funds` 列表是硬编码的，修改回测目标需直接编辑此列表。
- **定投金额常量**：`strategy_dingtou.py:13` 的 `MONEY_PER_MONTH_PER_FUND = 4000.0` 是全局常量。

## 策略扩展

继承 `StrategyInterface`，实现 `run()` 方法即可添加新策略。`run()` 返回值含义：
- 正数：买入金额
- 负数：卖出份额
- 0：不操作

注意：`back_tracking_deals.py` 中的 `MODE_SELECTED_ONLY` 开关控制是只跑精选基金还是全部基金，默认 `True`。

## 数据流

```
东方财富API → FundDownloader → .fund_cache/ (JSON缓存)
                                    ↓
                              BackTrackingDeal.run(策略)
                                    ↓
                         profits[] → CSV输出 (result/)
                                    → 图表 (profit.png)
```
