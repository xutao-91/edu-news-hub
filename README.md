# 🇺🇸 美国教育新闻动态 | Education News Hub

<div align="center">

<img src="https://img.shields.io/badge/数据来源-真实新闻抓取-brightgreen" alt="数据来源">
<img src="https://img.shields.io/badge/自动更新-每日10:00%20CDT-blue" alt="自动更新">
<img src="https://img.shields.io/badge/覆盖范围-中西部11州-green" alt="覆盖范围">

**每日自动更新的美国教育新闻聚合平台，聚焦中西部11州**

🌐 **[在线访问](https://xutao-91.github.io/edu-news-hub/)** | 📝 **[数据来源](./data/)**

</div>

---

## ✅ 真实新闻保证

| 特性 | 说明 |
|------|------|
| **真实抓取** | 使用Tavily API每日抓取115+教育新闻源 |
| **真实链接** | 所有新闻链接均可点击，跳转至原始新闻页面 |
| **真实日期** | 从原文中自动提取发布日期 |
| **智能筛选** | 联邦政策全收录 + 中西部11州新闻筛选 |

---

## 📋 功能特点

- 📆 **日期选择** - 选择任意日期查看当天新闻
- 🏷️ **分类标签** - 按类别快速筛选
- 📱 **响应式设计** - 支持手机、平板、电脑访问
- 🔄 **自动更新** - 每日10:00 CDT自动抓取最新新闻
- 📊 **统计分析** - 显示新闻数量、历史天数等统计信息

---

## 🗺️ 覆盖范围

**中西部11州：**
- IL（伊利诺伊）| IN（印第安纳）| IA（爱荷华）| MI（密歇根）| MO（密苏里）
- MN（明尼苏达）| KS（堪萨斯）| WI（威斯康星）| NE（内布拉斯加）
- SD（南达科他）| ND（北达科他）

**新闻类型：**
- 联邦政策
- AI教育
- 高等教育
- 师资问题
- 国际学生
- STEM教育
- K-12教育

---

## 🚀 自动更新机制

### 时间安排
- **每天上午 10:00 CDT**自动运行
- Cron表达式：`0 15 * * *` (UTC时间)

### 更新流程
```
10:00 CDT
    ↓
Tavily API搜索115+新闻源
    ↓
筛选联邦政策 + 中西部11州
    ↓
提取原文日期和内容
    ↓
分类整理
    ↓
推送GitHub
    ↓
GitHub Pages自动部署
    ↓
✅ 网站更新完成
```

---

## 🔧 技术栈

- **前端**：HTML5 + Tailwind CSS + Vanilla JS
- **数据获取**：Tavily API (实时新闻抓取)
- **部署**：GitHub Pages
- **自动化**：GitHub Actions + Cron
- **数据存储**：JSON文件，每日一个文件

---

## 📚 项目结构

```
edu-news-hub/
├── index.html          # 主页面
├── app.js              # 前端逻辑
├── data/               # 新闻数据
│   ├── index.json      # 日期索引
│   └── YYYY-MM-DD.json # 每日新闻（真实抓取）
├── scripts/            # 抓取脚本
├── .github/workflows/  # 自动更新工作流
└── README.md
```

---

## 📋 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2026-03-18 | ✓ 切换至真实新闻抓取模式，所有链接可点击 |
| 2026-03-17 | 项目上线，支持日期选择 |

---

## 👨‍💻 关于

**🦅 Open Claw** - 您的教育政策调研员

- 深耕教育外交领域15年+
- 长期跟踪UNESCO、OECD、World Bank等国际组织教育动态
- 监控美国Dept of Education、白宫、NSF等主要国家教育政策

---

<div align="center">

**由 Open Claw 真实抓取 · 每日10:00 CDT自动更新**

</div>
