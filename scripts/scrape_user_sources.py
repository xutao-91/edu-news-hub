#!/usr/bin/env python3
"""
从用户提供的113个权威来源抓取教育新闻
只访问用户指定的来源，不编造任何新闻
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import sys

# 用户来源库 - 高优先级前20个
USER_SOURCES = [
    {
        "id": "edweek",
        "name": "Education Week",
        "url": "https://www.edweek.org",
        "rss": "https://www.edweek.org/feeds/rss.xml",
        "type": "rss",
        "priority": 1
    },
    {
        "id": "chronicle", 
        "name": "Chronicle of Higher Education",
        "url": "https://www.chronicle.com",
        "rss": "https://www.chronicle.com/rss",
        "type": "rss",
        "priority": 1
    },
    {
        "id": "insidehighered",
        "name": "Inside Higher Ed",
        "url": "https://www.insidehighered.com",
        "rss": "https://www.insidehighered.com/rss.xml",
        "type": "rss",
        "priority": 1
    },
    {
        "id": "edgov",
        "name": "U.S. Department of Education",
        "url": "https://www.ed.gov/news",
        "type": "html",
        "priority": 1
    },
    {
        "id": "brookings",
        "name": "Brookings Institution",
        "url": "https://www.brookings.edu/topics/education-2/",
        "type": "html",
        "priority": 1
    },
    {
        "id": "csis",
        "name": "CSIS",
        "url": "https://www.csis.org/analysis",
        "type": "html",
        "priority": 2
    },
    {
        "id": "pew",
        "name": "Pew Research Center",
        "url": "https://www.pewresearch.org/publications/",
        "type": "html",
        "priority": 1
    },
    {
        "id": "nasbe",
        "name": "NASBE",
        "url": "https://www.nasbe.org/newsroom/",
        "type": "html",
        "priority": 2
    },
    {
        "id": "futureed",
        "name": "FutureEd",
        "url": "https://www.future-ed.org/legislative-tracker-2026-state-ai-in-education-bills/",
        "type": "html",
        "priority": 2
    },
    {
        "id": "nafsa",
        "name": "NAFSA",
        "url": "https://www.nafsa.org/blog",
        "type": "html",
        "priority": 2
    }
]

class UserSourceScraper:
    """用户来源抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.results = []
        
    def scrape_rss_source(self, source):
        """从RSS源抓取"""
        try:
            import feedparser
            feed = feedparser.parse(source['rss'])
            
            articles = []
            for entry in feed.entries[:5]:  # 每个来源取前5条
                # 提取日期
                date_str = entry.get('published', entry.get('updated', ''))
                
                # 只保留最近7天的
                if not self.is_recent_date(date_str):
                    continue
                
                articles.append({
                    'title': entry.title,
                    'url': entry.link,
                    'date': date_str,
                    'source': source['name'],
                    'summary': entry.get('summary', '')[:300],
                    'source_id': source['id']
                })
            
            print(f"  ✅ {source['name']}: {len(articles)}条")
            return articles
            
        except Exception as e:
            print(f"  ❌ {source['name']}: {e}")
            return []
    
    def scrape_html_source(self, source):
        """从HTML页面抓取"""
        try:
            response = self.session.get(source['url'], timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            
            # 根据不同来源使用不同的提取规则
            if source['id'] == 'edgov':
                # ED.gov 提取规则
                for item in soup.find_all('div', class_='news-item')[:5]:
                    title_elem = item.find('h3') or item.find('h2')
                    link_elem = item.find('a')
                    date_elem = item.find('time') or item.find('span', class_='date')
                    
                    if title_elem and link_elem:
                        articles.append({
                            'title': title_elem.get_text().strip(),
                            'url': link_elem.get('href', ''),
                            'date': date_elem.get_text().strip() if date_elem else '',
                            'source': source['name'],
                            'source_id': source['id']
                        })
            
            elif source['id'] == 'brookings':
                # Brookings 提取规则
                for item in soup.find_all('article')[:5]:
                    title_elem = item.find('h3') or item.find('h2')
                    link_elem = item.find('a')
                    
                    if title_elem and link_elem:
                        articles.append({
                            'title': title_elem.get_text().strip(),
                            'url': link_elem.get('href', ''),
                            'date': '',
                            'source': source['name'],
                            'source_id': source['id']
                        })
            
            print(f"  ✅ {source['name']}: {len(articles)}条")
            return articles
            
        except Exception as e:
            print(f"  ❌ {source['name']}: {e}")
            return []
    
    def is_recent_date(self, date_str, days=7):
        """检查日期是否在最近N天内"""
        if not date_str:
            return True  # 没有日期默认保留
        
        try:
            from dateutil import parser
            date = parser.parse(date_str)
            delta = datetime.now() - date
            return delta.days <= days
        except:
            return True  # 解析失败默认保留
    
    def categorize_news(self, article):
        """自动分类新闻"""
        title = article.get('title', '').lower()
        
        categories = {
            'federal': ['federal', 'department of education', 'congress', 'white house'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'chatgpt'],
            'higher': ['university', 'college', 'higher education', 'enrollment'],
            'teacher': ['teacher', 'educator', 'faculty', 'shortage'],
            'international': ['international', 'visa', 'f-1', 'foreign student'],
            'k12': ['k-12', 'elementary', 'secondary', 'school district']
        }
        
        for cat, keywords in categories.items():
            if any(kw in title for kw in keywords):
                return cat
        return 'general'
    
    def compile_output(self, articles):
        """编译输出格式"""
        news_list = []
        for article in articles[:25]:  # 最多25条
            news_list.append({
                'category': self.categorize_news(article),
                'title': article['title'],
                'source': article['source'],
                'original_date': article.get('date', ''),
                'summary': article.get('summary', '')[:400],
                'url': article['url'],
                'fetched_from': 'user_source',
                'source_id': article.get('source_id', '')
            })
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'Open Claw - User Sources Only',
            'source_method': '从用户提供的113个权威来源抓取',
            'total_news': len(news_list),
            'categories': self.count_categories(news_list),
            'news': news_list
        }
    
    def count_categories(self, news_list):
        """统计分类数量"""
        counts = {}
        for item in news_list:
            cat = item.get('category', 'general')
            counts[cat] = counts.get(cat, 0) + 1
        return counts
    
    def run(self):
        """运行抓取"""
        print("="*70)
        print("🚀 从用户提供的权威来源抓取教育新闻")
        print("="*70)
        print()
        
        # 按优先级排序
        sources = sorted(USER_SOURCES, key=lambda x: x.get('priority', 99))
        
        all_articles = []
        for source in sources:
            print(f"📡 {source['name']}")
            
            if source.get('type') == 'rss' and source.get('rss'):
                articles = self.scrape_rss_source(source)
            else:
                articles = self.scrape_html_source(source)
            
            all_articles.extend(articles)
        
        print()
        print(f"📊 总计获取: {len(all_articles)} 条")
        
        # 编译输出
        output = self.compile_output(all_articles)
        
        # 保存
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_file = f'data/{date_str}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已保存: {output_file}")
        print(f"   新闻数: {output['total_news']}")
        print(f"   分类: {output['categories']}")
        
        return output

if __name__ == '__main__':
    scraper = UserSourceScraper()
    scraper.run()
