# A股分析工具

配合Claude进行A股分析，支持全自动获取行情

---

## 功能特点

- ✅ **自动获取行情**：GitHub Actions每日自动运行
- ✅ **自动提交**：数据自动推送到仓库
- ✅ **Claude分析**：发链接即可获取分析

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `.github/workflows/fetch_market.yml` | GitHub Actions配置 |
| `fetch_market_auto.py` | 自动获取脚本（Actions用） |
| `fetch_market.py` | 手动获取脚本（本地用） |
| `run_fetch.bat` | 本地手动获取行情 |
| `git_push.bat` | 本地手动提交 |
| `about_me.md` | **投资者画像（必填）** |
| `portfolio.md` | 当前持仓 |
| `watchlist.md` | 观察清单 |
| `trading_journal.md` | 交易日记 |
| `ask_claude.md` | 问Claude模板 |

---

## 首次配置（重要！）

### 第1步：上传文件到GitHub

1. 打开 https://github.com/ZusyLu/learn
2. 删除仓库中旧文件（如有）
3. 点击 `Add file` → `Upload files`
4. 把解压后的**所有文件和文件夹**拖入上传
5. 点击 `Commit changes`

**注意**：`.github` 文件夹也要上传！

### 第2步：启用GitHub Actions

1. 打开仓库页面
2. 点击顶部 `Actions` 标签
3. 如果看到提示，点击 `I understand my workflows, go ahead and enable them`
4. 点击左侧 `Fetch A-Share Market Data`
5. 点击 `Enable workflow`

### 第3步：设置仓库权限

1. 点击仓库 `Settings`（设置）
2. 左侧找到 `Actions` → `General`
3. 滚动到底部 `Workflow permissions`
4. 选择 `Read and write permissions`
5. 点击 `Save`

### 第4步：填写你的信息

用GitHub网页编辑或本地编辑后上传：
- `about_me.md` - **详细填写你的投资风格**
- `portfolio.md` - 填写持仓

---

## 自动运行说明

配置完成后：

- **自动运行时间**：每个交易日北京时间 15:35
- **自动生成文件**：`market_YYYY-MM-DD.md`
- **自动提交**：数据自动推送到仓库

你只需要：
1. 有交易时更新 `portfolio.md`
2. 发GitHub链接给Claude分析

---

## 手动触发（测试用）

1. 打开仓库 `Actions` 页面
2. 点击左侧 `Fetch A-Share Market Data`
3. 点击右侧 `Run workflow`
4. 点击绿色 `Run workflow` 按钮
5. 等待1-2分钟，刷新仓库查看是否生成了market文件

---

## 问Claude分析

每天发这段话给Claude：

```
分析我的A股持仓：
https://github.com/ZusyLu/learn

读取 about_me.md, portfolio.md, 今日market文件
给出：市场主线、持仓风险、明日建议
```

---

## 本地使用（可选）

如果你想在本地电脑手动获取数据：

1. 安装 Python 和 Git
2. 双击 `run_fetch.bat` 获取行情
3. 双击 `git_push.bat` 提交

---

## 目录结构

```
learn/
├── .github/
│   └── workflows/
│       └── fetch_market.yml   ← Actions配置
├── fetch_market_auto.py       ← 自动脚本
├── fetch_market.py            ← 手动脚本
├── run_fetch.bat              ← 本地获取
├── git_push.bat               ← 本地提交
├── git_setup.bat              ← Git配置
├── about_me.md                ← 投资者画像
├── portfolio.md               ← 持仓
├── watchlist.md               ← 观察清单
├── trading_journal.md         ← 交易日记
├── ask_claude.md              ← 问Claude模板
├── README.md                  ← 本文件
└── market_YYYY-MM-DD.md       ← 每日行情（自动生成）
```

---

## 常见问题

**Q: Actions没有运行？**
- 检查是否启用了workflow
- 检查仓库权限是否设置为Read and write

**Q: 周末会运行吗？**
- 不会，只在周一到周五运行

**Q: 如何查看运行日志？**
- 点击Actions → 点击某次运行 → 查看日志

**Q: 节假日会运行吗？**
- 会运行，但可能获取不到当日数据（会用上一交易日）
