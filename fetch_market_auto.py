# -*- coding: utf-8 -*-
"""
A股行情自动获取脚本 - GitHub Actions版
自动运行，无需交互
"""

import os
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

def safe_get(func, default=None):
    """安全执行函数"""
    try:
        return func()
    except Exception as e:
        print(f"[WARNING] {e}")
        return default

def get_index_data():
    """获取主要指数"""
    print("Fetching index data...")
    def fetch():
        df = ak.stock_zh_index_spot_em()
        targets = ['上证指数', '深证成指', '创业板指', '科创50', '沪深300', '中证500']
        return df[df['名称'].isin(targets)][['名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额']]
    return safe_get(fetch)

def get_sector_data():
    """获取板块数据"""
    print("Fetching sector data...")
    def fetch():
        df = ak.stock_board_industry_name_em()
        df = df[['板块名称', '最新价', '涨跌幅', '主力净流入-净额']]
        df = df.sort_values('涨跌幅', ascending=False)
        return df.head(5), df.tail(5).sort_values('涨跌幅')
    result = safe_get(fetch, (None, None))
    return result if result else (None, None)

def get_north_flow():
    """获取北向资金"""
    print("Fetching north flow...")
    def fetch():
        df = ak.stock_hsgt_north_net_flow_in_em(symbol="北向")
        if not df.empty:
            latest = df.iloc[-1]
            return {'date': str(latest['date']), 'value': latest['value']}
        return None
    return safe_get(fetch)

def get_hot_stocks():
    """获取涨跌幅榜"""
    print("Fetching top gainers/losers...")
    def fetch():
        df = ak.stock_zh_a_spot_em()
        df = df[['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '换手率']]
        df = df[~df['名称'].str.contains('ST|N |C ', na=False)]
        df = df.sort_values('涨跌幅', ascending=False)
        return df.head(10), df.tail(10).sort_values('涨跌幅')
    result = safe_get(fetch, (None, None))
    return result if result else (None, None)

def get_limit_count():
    """获取涨跌停数量"""
    print("Fetching limit up/down...")
    def fetch():
        today = datetime.now().strftime('%Y%m%d')
        try:
            df_up = ak.stock_zt_pool_em(date=today)
            up = len(df_up) if df_up is not None and not df_up.empty else 0
        except:
            up = "N/A"
        try:
            df_down = ak.stock_zt_pool_dtgc_em(date=today)
            down = len(df_down) if df_down is not None and not df_down.empty else 0
        except:
            down = "N/A"
        return up, down
    return safe_get(fetch, ("N/A", "N/A"))

def get_concept_hot():
    """获取热门概念板块"""
    print("Fetching hot concepts...")
    def fetch():
        df = ak.stock_board_concept_name_em()
        df = df[['板块名称', '最新价', '涨跌幅', '主力净流入-净额']]
        df = df.sort_values('涨跌幅', ascending=False)
        return df.head(10)
    return safe_get(fetch)

def generate_report():
    """生成报告"""
    
    # 使用北京时间
    utc_now = datetime.utcnow()
    beijing_now = utc_now + timedelta(hours=8)
    today = beijing_now.strftime('%Y-%m-%d')
    now_str = beijing_now.strftime('%Y-%m-%d %H:%M:%S')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[beijing_now.weekday()]
    
    md = f"""# A股市场日报

> 日期：{today} {weekday}
> 自动生成：{now_str} (北京时间)
> 数据来源：东方财富

---

## 主要指数

"""
    
    # 指数
    index_data = get_index_data()
    if index_data is not None and not index_data.empty:
        md += "| 指数 | 最新价 | 涨跌幅 | 涨跌额 | 成交量(手) | 成交额(元) |\n"
        md += "|------|--------|--------|--------|------------|------------|\n"
        for _, row in index_data.iterrows():
            pct = row['涨跌幅']
            emoji = "🔴" if pct >= 0 else "🟢"
            md += f"| {row['名称']} | {row['最新价']:.2f} | {emoji} {pct:+.2f}% | {row['涨跌额']:+.2f} | {row['成交量']:,.0f} | {row['成交额']:,.0f} |\n"
    else:
        md += "(数据获取失败)\n"
    
    # 板块
    md += "\n---\n\n## 行业板块\n\n"
    top_sectors, bottom_sectors = get_sector_data()
    
    if top_sectors is not None and not top_sectors.empty:
        md += "### 领涨行业 TOP5\n\n"
        md += "| 板块 | 涨跌幅 | 主力净流入(亿) |\n"
        md += "|------|--------|----------------|\n"
        for _, row in top_sectors.iterrows():
            flow = row['主力净流入-净额'] / 100000000
            md += f"| {row['板块名称']} | 🔴 {row['涨跌幅']:+.2f}% | {flow:+.2f} |\n"
    
    if bottom_sectors is not None and not bottom_sectors.empty:
        md += "\n### 领跌行业 TOP5\n\n"
        md += "| 板块 | 涨跌幅 | 主力净流入(亿) |\n"
        md += "|------|--------|----------------|\n"
        for _, row in bottom_sectors.iterrows():
            flow = row['主力净流入-净额'] / 100000000
            md += f"| {row['板块名称']} | 🟢 {row['涨跌幅']:+.2f}% | {flow:+.2f} |\n"
    
    # 概念板块
    md += "\n---\n\n## 热门概念 TOP10\n\n"
    concepts = get_concept_hot()
    if concepts is not None and not concepts.empty:
        md += "| 概念 | 涨跌幅 | 主力净流入(亿) |\n"
        md += "|------|--------|----------------|\n"
        for _, row in concepts.iterrows():
            flow = row['主力净流入-净额'] / 100000000
            emoji = "🔴" if row['涨跌幅'] >= 0 else "🟢"
            md += f"| {row['板块名称']} | {emoji} {row['涨跌幅']:+.2f}% | {flow:+.2f} |\n"
    
    # 资金流向
    md += "\n---\n\n## 资金流向\n\n"
    north = get_north_flow()
    if north:
        emoji = "🔴 净流入" if north['value'] >= 0 else "🟢 净流出"
        md += f"**北向资金**：{emoji} {abs(north['value']):.2f} 亿元\n\n"
    else:
        md += "**北向资金**：数据获取失败\n\n"
    
    up_count, down_count = get_limit_count()
    md += f"**涨停家数**：{up_count}\n\n"
    md += f"**跌停家数**：{down_count}\n\n"
    
    # 涨跌幅榜
    md += "---\n\n## 涨幅榜 TOP10\n\n"
    top_stocks, bottom_stocks = get_hot_stocks()
    
    if top_stocks is not None and not top_stocks.empty:
        md += "| 代码 | 名称 | 现价 | 涨跌幅 | 换手率 |\n"
        md += "|------|------|------|--------|--------|\n"
        for _, row in top_stocks.iterrows():
            md += f"| {row['代码']} | {row['名称']} | {row['最新价']:.2f} | 🔴 {row['涨跌幅']:+.2f}% | {row['换手率']:.2f}% |\n"
    
    if bottom_stocks is not None and not bottom_stocks.empty:
        md += "\n## 跌幅榜 TOP10\n\n"
        md += "| 代码 | 名称 | 现价 | 涨跌幅 | 换手率 |\n"
        md += "|------|------|------|--------|--------|\n"
        for _, row in bottom_stocks.iterrows():
            md += f"| {row['代码']} | {row['名称']} | {row['最新价']:.2f} | 🟢 {row['涨跌幅']:+.2f}% | {row['换手率']:.2f}% |\n"
    
    md += """
---

## 我的观察（手动填写）

### 今日盘面感受


### 关注的机会


### 风险点


"""
    
    return md, today

def main():
    print("=" * 50)
    print("  A-Share Market Data Fetcher (Auto)")
    print("=" * 50)
    print()
    
    report, today = generate_report()
    
    filename = f"market_{today}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print(f"[DONE] Saved: {filename}")
    print()

if __name__ == "__main__":
    main()
