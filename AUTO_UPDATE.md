# 📰 教育新闻自动更新说明

## ⏰ 更新时间

**每天上午 10:00 CDT（美国中部时间）**

- Cron表达式: `0 15 * * *` (UTC时间，对应CDT 10:00)
- 自动推送到: https://xutao-91.github.io/edu-news-hub/

## 🔄 更新流程

1. **10:00 CDT** - Cron定时触发
2. **拉取代码** - 从GitHub获取最新版本
3. **生成新闻** - 运行新闻抓取脚本
4. **更新索引** - 更新日期索引文件
5. **推送GitHub** - 自动提交并部署

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `scripts/auto_update_news.sh` | 自动更新主脚本 |
| `scripts/generate_daily_news.py` | 新闻生成脚本 |
| `edu-news-update.log` | 更新日志 |

## 🛠️ 手动触发

如需立即更新，运行：
```bash
/root/.openclaw/workspace/scripts/auto_update_news.sh
```

## 📊 更新记录

查看日志：
```bash
tail -f /root/.openclaw/workspace/edu-news-update.log
```

## 📝 注意事项

- 自动更新使用GitHub Token进行推送
- 如GitHub Token过期需要重新配置
- 更新失败会记录错误日志
