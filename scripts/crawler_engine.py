#!/usr/bin/env python3
"""
教育新闻爬虫引擎 - 从网页源码提取精准信息
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import json

class EducationNewsCrawler:
    """教育新闻爬虫引擎"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.history_file = '/root/.openclaw/workspace/edu-news-hub/history/news_history.json'
        self.load_history()
        
    def load_history(self):
        """加载历史记录"""
        try:
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        except:
            self.history = {"entries": [], "url_index": {}}
    
    def save_history(self):
        """保存历史记录"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def url_exists(self, url):
        """检查URL是否已存在"""
        return url in self.history.get('url_index', {})
    
    def add_to_history(self, entry):
        """添加到历史记录"""
        if entry['url'] not in self.history.get('url_index', {}):
            self.history['entries'].append(entry)
            self.history['url_index'][entry['url']] = len(self.history['entries']) - 1
            self.history['total_entries'] = len(self.history['entries'])
            return True
        return False
    
    def parse_date(self, date_str):
        """解析各种日期格式"""
        formats = [
            "%B %d, %Y",      # February 23, 2026
            "%b %d, %Y",      # Feb 23, 2026
            "%Y-%m-%d",       # 2026-02-23
            "%Y-%m-%dT%H:%M:%S",  # ISO格式
            "%m/%d/%Y",       # 02/23/2026
            "%d %B %Y",       # 23 February 2026
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        # 尝试从文本中提取日期
        patterns = [
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                try:
                    return datetime.strptime(match.group(0), "%B %d, %Y")
                except:
                    pass
        
        return None
    
    def is_recent_date(self, date_obj, days=7):
        """检查日期是否在指定天数内"""
        if not date_obj:
            return False
        today = datetime.now()
        delta = today - date_obj
        return 0 <= delta.days <= days
    
    def crawl_edweek(self, url):
        """爬取 Education Week"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取日期 - 从作者区域
            date_elem = soup.find('span', class_='m-article-title__author')
            date_str = None
            if date_elem:
                text = date_elem.get_text()
                # 匹配 "— February 23, 2026" 格式
                match = re.search(r'—\s+([A-Za-z]+ \d{1,2}, \d{4})', text)
                if match:
                    date_str = match.group(1)
            
            # 备用：从meta标签
            if not date_str:
                meta = soup.find('meta', property='article:published_time')
                if meta:
                    date_str = meta.get('content', '').split('T')[0]
            
            # 提取标题
            title_elem = soup.find('h1', class_='m-article-title__text')
            title = title_elem.get_text().strip() if title_elem else None
            
            # 提取内容摘要
            content_elem = soup.find('div', class_='m-article-content')
            content = content_elem.get_text().strip()[:1000] if content_elem else None
            
            return {
                'title': title,
                'date_str': date_str,
                'date_parsed': self.parse_date(date_str) if date_str else None,
                'content': content,
                'url': url,
                'source': 'Education Week'
            }
        except Exception as e:
            print(f"❌ EdWeek爬取失败 {url}: {e}")
            return None
    
    def crawl_wordpress(self, url):
        """爬取 WordPress 网站"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取日期
            date_str = None
            meta = soup.find('meta', property='article:published_time')
            if meta:
                date_str = meta.get('content', '').split('T')[0]
            
            if not date_str:
                time_elem = soup.find('time', class_='entry-date')
                if time_elem:
                    date_str = time_elem.get_text().strip()
            
            # 提取标题
            title_elem = soup.find('h1', class_='entry-title') or soup.find('h1', class_='article-title')
            title = title_elem.get_text().strip() if title_elem else None
            
            # 提取内容
            content_elem = soup.find('div', class_='entry-content')
            content = content_elem.get_text().strip()[:1000] if content_elem else None
            
            return {
                'title': title,
                'date_str': date_str,
                'date_parsed': self.parse_date(date_str) if date_str else None,
                'content': content,
                'url': url,
                'source': 'WordPress Site'
            }
        except Exception as e:
            print(f"❌ WordPress爬取失败 {url}: {e}")
            return None
    
    def crawl_generic(self, url, source_name="Unknown"):
        """通用爬虫"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试多种日期提取方式
            date_str = None
            
            # 1. meta标签
            meta = soup.find('meta', property='article:published_time')
            if meta:
                date_str = meta.get('content', '')
            
            # 2. time标签
            if not date_str:
                time_elem = soup.find('time')
                if time_elem:
                    date_str = time_elem.get('datetime') or time_elem.get_text().strip()
            
            # 3. 常见日期类名
            if not date_str:
                for cls in ['date', 'published', 'post-date', 'entry-date']:
                    elem = soup.find(class_=cls)
                    if elem:
                        date_str = elem.get_text().strip()
                        break
            
            # 提取标题
            title = None
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text().strip()
            
            # 提取内容
            content = None
            for cls in ['content', 'entry-content', 'article-content', 'post-content']:
                elem = soup.find(class_=cls)
                if elem:
                    content = elem.get_text().strip()[:1000]
                    break
            
            return {
                'title': title,
                'date_str': date_str,
                'date_parsed': self.parse_date(date_str) if date_str else None,
                'content': content,
                'url': url,
                'source': source_name
            }
        except Exception as e:
            print(f"❌ 通用爬取失败 {url}: {e}")
            return None
    
    def crawl_cato(self, url):
        """爬取 Cato Institute 网站"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取日期
            date_str = None
            date_elem = soup.find('span', class_='date-time__date--default')
            if date_elem:
                date_str = date_elem.get_text().strip()
            
            # 备用：从meta标签
            if not date_str:
                meta = soup.find('meta', property='article:published_time')
                if meta:
                    date_str = meta.get('content', '').split('T')[0]
            
            # 提取标题
            title_elem = soup.find('h1', class_='h2') or soup.find('h1', property='headline')
            title = title_elem.get_text().strip() if title_elem else None
            
            # 提取内容
            content_elem = soup.find('div', class_='blog-page__content')
            content = content_elem.get_text().strip()[:1000] if content_elem else None
            
            return {
                'title': title,
                'date_str': date_str,
                'date_parsed': self.parse_date(date_str) if date_str else None,
                'content': content,
                'url': url,
                'source': 'Cato Institute'
            }
        except Exception as e:
            print(f"❌ Cato爬取失败 {url}: {e}")
            return None
    
    def crawl_by_source(self, url, source_type, source_name):
        """根据来源类型选择爬虫"""
        crawlers = {
            'edweek': self.crawl_edweek,
            'cato': self.crawl_cato,
            'wordpress': self.crawl_wordpress,
        }
        
        crawler = crawlers.get(source_type, self.crawl_generic)
        return crawler(url) if crawler != self.crawl_generic else crawler(url, source_name)


if __name__ == '__main__':
    # 测试
    crawler = EducationNewsCrawler()
    
    # 测试 EdWeek
    test_url = "https://www.edweek.org/policy-politics/the-education-department-will-send-more-of-its-programs-to-other-agencies/2026/02"
    result = crawler.crawl_edweek(test_url)
    if result:
        print("✅ EdWeek 测试结果:")
        print(f"  标题: {result['title'][:60]}...")
        print(f"  日期字符串: {result['date_str']}")
        print(f"  解析日期: {result['date_parsed']}")
