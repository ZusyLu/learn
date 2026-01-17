# -*- coding: utf-8 -*-
"""
A股行情自动获取脚本 v2.0
双击 run_fetch.bat 运行
"""

import os
import sys
from datetime import datetime

def check_and_install_packages():
    """检查并安装所需的包"""
    required = ['akshare', 'pandas']
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"[OK] {pkg}")
        except ImportError:
            print(f"[Installing] {pkg}...")
            ret = os.system(f'"{sys.executable}" -m pip install {pkg} -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet')
            if ret != 0:
                print(f"[WARNING] Failed to install {pkg}, trying default source...")
                os.system(f'"{sys.executable}" -m pip install {pkg} --quiet')
    
    print("\n[OK] All dependencies ready!\n")

print("=" * 50)
print("       Stock Data Fetcher v2.0")
print("=" * 50)
print()
print("Checking dependencies...")
check_and_install_packages()

import akshare as ak
import pandas as pd

def safe_get(func, default=None):
    """安全执行函数，出错返回默认值"""
    try:
        return func()
    except Exception as e:
        print(f"[WARNING] {e}")
        return default

def get_index_data():
    """获取主要指数数据"""
    print("Fetching index data...")
    def fetch():
        df = ak.stock_zh_index_spot_em()
        targets = ['上证指数', '深证成指', '创业板指', '科创50', '沪深300', '中证500']
        return df[df['名称'].isin(targets)][['名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额']]
    return safe_get(fetch)

def get_sector_data():
    """获取板块涨跌数据"""
    print("Fetching sector data...")
    def fetch():
        df = ak.stock_board_industry_name_em()
        df = df[['板块名称', '最新价', '涨跌幅', '主力净流入-净额']]
        df = df.sort_values('涨跌幅', ascending=False)
        return df.head(5), df.tail(5).sort_values('涨跌幅')
    result = safe_get(fetch, (None, None))
    return result if result else (None, None)

def get_north_flow():
    """获取北向资金数据"""
    print("Fetching north flow data...")
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
    print("Fetching limit up/down count...")
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

def generate_report():
    """生成Markdown报告"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[datetime.now().weekday()]
    
    md = f"""# A股市场日报

> 日期：{today} {weekday}
> 生成时间：{now_str}

---

## 主要指数

"""
    
    # 指数数据
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
    
    # 板块数据
    md += "\n---\n\n## 板块表现\n\n"
    top_sectors, bottom_sectors = get_sector_data()
    
    if top_sectors is not None and not top_sectors.empty:
        md += "### 领涨板块 TOP5\n\n"
        md += "| 板块 | 涨跌幅 | 主力净流入(亿) |\n"
        md += "|------|--------|----------------|\n"
        for _, row in top_sectors.iterrows():
            flow = row['主力净流入-净额'] / 100000000
            md += f"| {row['板块名称']} | 🔴 {row['涨跌幅']:+.2f}% | {flow:+.2f} |\n"
    
    if bottom_sectors is not None and not bottom_sectors.empty:
        md += "\n### 领跌板块 TOP5\n\n"
        md += "| 板块 | 涨跌幅 | 主力净流入(亿) |\n"
        md += "|------|--------|----------------|\n"
        for _, row in bottom_sectors.iterrows():
            flow = row['主力净流入-净额'] / 100000000
            md += f"| {row['板块名称']} | 🟢 {row['涨跌幅']:+.2f}% | {flow:+.2f} |\n"
    
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
    
    return md

def main():
    now = datetime.now()
    if now.weekday() >= 5:
        print("[NOTE] Today is weekend. Data may be from last trading day.\n")
    
    print("Generating report...\n")
    
    report = generate_report()
    
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"market_{today}.md"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print("=" * 50)
    print(f"[DONE] Report saved: {filename}")
    print("=" * 50)
    print()
    print("Next steps:")
    print("  1. Open the report and fill 'My Notes' section")
    print("  2. Update portfolio.md if you traded today")
    print("  3. Run git_push.bat to upload to GitHub")
    print("  4. Send GitHub link to Claude for analysis")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("\nPress Enter to exit...")
