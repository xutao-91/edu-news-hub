# 🇺🇸 美国教育新闻动态 | Education News Hub

<div align="center">

<img src="https://img.shields.io/badge/自动更新-每日10:00%20CDT-blue" alt="自动更新">
<img src="https://img.shields.io/badge/覆盖范围-中西部11州-green" alt="覆盖范围">
<img src="https://img.shields.io/badge/新闻源-115+-orange" alt="新闻源">

**每日自动更新的美国教育新闻聚合平台，聚焦中西部11州**

[🌐 在线访问](https://xutao-91.github.io/edu-news-hub) | [📊 数据来源](./data/)

</div>

---

## 📋 功能特点

- 📅 **日期选择** - 选择任意日期查看当天新闻
- 🏷️ **分类标签** - 按类别快速筛选（联邦政策、AI教育、高等教育等）
- 📱 **响应式设计** - 支持手机、平板、电脑访问
- 🔄 **自动更新** - 每日10:00 CDT自动抓取最新新闻
- 📊 **统计分析** - 显示新闻数量、历史天数等统计信息

## 🗺️ 覆盖范围

**中西部11州：**
- IL（伊利诺伊）
- IN（印第安纳）
- IA（爱荷华）
- MI（密歇根）
- MO（密苏里）
- MN（明尼苏达）
- KS（堪萨斯）
- WI（威斯康星）
- NE（内布拉斯加）
- SD（南达科他）
- ND（北达科他）

**新闻类型：**
- 联邦政策
- AI教育
- 高等教育
- 师资问题
- 国际学生
- STEM教育
- K-12教育

## 📁 项目结构

```
edu-news-hub/
├── index.html          # 主页面
├── app.js              # 前端逻辑
├── data/               # 新闻数据
│   ├── index.json      # 日期索引
│   └── YYYY-MM-DD.json # 每日新闻
├── .github/
│   └── workflows/      # 自动更新工作流
└── README.md
```

## 🔄 自动更新机制

本项目使用 GitHub Actions 每日自动更新：

1. **定时触发** - 每天10:00 CDT自动运行
2. **数据抓取** - 从115+教育新闻源抓取最新动态
3. **智能筛选** - 按中西部11州和联邦政策筛选
4. **生成文件** - 生成JSON格式的新闻数据
5. **自动提交** - 推送到GitHub仓库并部署

## 📊 数据来源

- Tavily AI Search API
- 美国教育部官网
- 各州教育部门网站
- 教育新闻媒体
- 高校官网新闻
- 研究机构报告

## 🛠️ 本地开发

```bash
# 克隆仓库
git clone https://github.com/xutao-91/edu-news-hub.git
cd edu-news-hub

# 启动本地服务器
python -m http.server 8000

# 访问 http://localhost:8000
```

## 📜 筛选原则

1. **联邦政策** - 全部收录
2. **全国性研究** - 涉及中西部任一州即收录
3. **州级新闻** - 仅限中西部11州
4. **时间限制** - 所有新闻日期不超过7天

## 🤖 技术栈

- **前端**: HTML5 + Tailwind CSS + Vanilla JS
- **部署**: GitHub Pages
- **自动化**: GitHub Actions
- **数据源**: Tavily AI Search API

## 📝 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2026-03-17 | 项目上线，首批10条新闻 |

## 👨‍💻 关于

**🦅 Open Claw** - 您的教育政策调研员

- 深耕教育外交领域15年+
- 长期跟踪UNESCO、OECD、World Bank等国际组织教育动态
- 监控美国Dept of Education、白宫、NSF等主要国家教育政策

---

<div align="center">

**Made with ❤️ by Open Claw**

</div>
