#!/usr/bin/env python3
"""
高级教育新闻爬虫 - 使用Playwright操作真实浏览器
突破反爬虫限制，实现高效抓取
"""
import asyncio
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
import random
import os

class AdvancedEducationCrawler:
    """高级教育新闻爬虫 - 使用Playwright"""
    
    def __init__(self):
        self.results = []
        
        # 使用相对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = os.path.dirname(script_dir)
        self.history_file = os.path.join(self.project_dir, 'history', 'news_history.json')
        self.sources_file = os.path.join(self.project_dir, 'sources', 'index.json')
        
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
            "%b. %d, %Y",     # Jan. 22, 2026
            "%Y-%m-%d",       # 2026-02-23
            "%Y-%m-%dT%H:%M:%S",  # ISO格式
            "%m/%d/%Y",       # 02/23/2026
            "%d %B %Y",       # 23 February 2026
            "%A, %B %d, %Y",  # Monday, January 5, 2026
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        return None
    
    def is_recent_date(self, date_obj, days=7):
        """检查日期是否在指定天数内"""
        if not date_obj:
            return False
        today = datetime.now()
        delta = today - date_obj
        return 0 <= delta.days <= days
    
    async def crawl_with_playwright(self, url, source_config):
        """使用Playwright爬取网页"""
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # 启动浏览器（无头模式）
            browser = await p.chromium.launch(headless=True)
            
            # 创建新页面
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # 访问页面
                print(f"  🌐 访问: {url[:60]}...")
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 随机等待，模拟人类行为
                await asyncio.sleep(random.uniform(2, 5))
                
                # 滚动页面
                await page.evaluate('window.scrollBy(0, 500)')
                await asyncio.sleep(random.uniform(1, 3))
                
                # 获取页面内容
                content = await page.content()
                
                # 提取数据
                result = self.extract_data(content, source_config, url)
                
                await browser.close()
                return result
                
            except Exception as e:
                print(f"  ❌ Playwright错误: {e}")
                await browser.close()
                return None
    
    def extract_data(self, html, source_config, url):
        """从HTML提取数据"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        crawler_type = source_config.get('crawler', 'generic')
        
        # 根据爬虫类型提取
        extractors = {
            'edweek': self._extract_edweek,
            'cato': self._extract_cato,
            'edgov': self._extract_edgov,
            'pew': self._extract_pew,
            'iowa': self._extract_iowa,
            'msu': self._extract_msu,
            'generic': self._extract_generic
        }
        
        extractor = extractors.get(crawler_type, self._extract_generic)
        return extractor(soup, url, source_config)
    
    def _extract_edweek(self, soup, url, config):
        """提取EdWeek数据"""
        # 日期
        date_elem = soup.find('span', class_='m-article-title__author')
        date_str = None
        if date_elem:
            text = date_elem.get_text()
            match = re.search(r'—\s+([A-Za-z]+ \d{1,2}, \d{4})', text)
            if match:
                date_str = match.group(1)
        
        # 标题
        title_elem = soup.find('h1', class_='m-article-title__text')
        title = title_elem.get_text().strip() if title_elem else None
        
        # 内容
        content_elem = soup.find('div', class_='m-article-content')
        content = content_elem.get_text().strip()[:1500] if content_elem else None
        
        return self._create_result(title, date_str, content, url, 'Education Week')
    
    def _extract_cato(self, soup, url, config):
        """提取CATO数据"""
        date_elem = soup.find('span', class_='date-time__date--default')
        date_str = date_elem.get_text().strip() if date_elem else None
        
        title_elem = soup.find('h1', class_='h2')
        title = title_elem.get_text().strip() if title_elem else None
        
        content_elem = soup.find('div', class_='blog-page__content')
        content = content_elem.get_text().strip()[:1500] if content_elem else None
        
        return self._create_result(title, date_str, content, url, 'Cato Institute')
    
    def _extract_edgov(self, soup, url, config):
        """提取ed.gov数据"""
        time_elem = soup.find('div', class_='field--name-published-at')
        date_str = None
        if time_elem:
            time_tag = time_elem.find('time')
            if time_tag and time_tag.get('datetime'):
                date_str = time_tag['datetime'].split('T')[0]
        
        title_elem = soup.find('h1', class_='ed-node-title') or soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else None
        
        content_elem = soup.find('div', class_='field--name-body')
        content = content_elem.get_text().strip()[:1500] if content_elem else None
        
        return self._create_result(title, date_str, content, url, 'U.S. Department of Education')
    
    def _extract_pew(self, soup, url, config):
        """提取Pew数据"""
        metadata = soup.find('div', class_='page-metadata__items')
        date_str = None
        if metadata:
            spans = metadata.find_all('span', class_='page-metadata__item')
            if len(spans) >= 2:
                date_str = spans[1].get_text().strip()
        
        title_elem = soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else None
        
        content_elem = soup.find('div', class_='article-content')
        content = content_elem.get_text().strip()[:1500] if content_elem else None
        
        return self._create_result(title, date_str, content, url, 'Pew Research Center')
    
    def _extract_iowa(self, soup, url, config):
        """提取Iowa数据"""
        time_elem = soup.find('div', class_='field--name-field-news__display-date')
        date_str = None
        if time_elem:
            time_tag = time_elem.find('time')
            if time_tag and time_tag.get('datetime'):
                date_str = time_tag['datetime'].split('T')[0]
        
        title_elem = soup.find('h1', class_='page-title') or soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else None
        
        content_elem = soup.find('div', class_='field--name-body')
        content = content_elem.get_text().strip()[:1500] if content_elem else None
        
        return self._create_result(title, date_str, content, url, 'Iowa Department of Education')
    
    def _extract_msu(self, soup, url, config):
        """提取MSU数据"""
        date_elem = soup.find('p', class_='dateline line') or soup.find('p', class_='dateline')
        date_str = None
        if date_elem:
            text = date_elem.get_text()
            match = re.search(r'([A-Za-z]+\.?\s+\d{1,2},\s+\d{4})', text)
            if match:
                date_str = match.group(1)
        
        title_elem = soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else None
        
        content_elem = soup.find('div', class_='field--name-body') or soup.find('article')
        content = content_elem.get_text().strip()[:1500] if content_elem else None
        
        return self._create_result(title, date_str, content, url, 'Michigan State University')
    
    def _extract_generic(self, soup, url, config):
        """通用提取"""
        # 尝试多种日期选择器
        date_str = None
        for selector in ['meta[property="article:published_time"]', 'time', '.date', '.published']:
            elem = soup.select_one(selector)
            if elem:
                if elem.get('content'):
                    date_str = elem['content'].split('T')[0]
                else:
                    date_str = elem.get_text().strip()
                break
        
        title_elem = soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else None
        
        content_elem = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        content = content_elem.get_text().strip()[:1500] if content_elem else None
        
        source_name = urlparse(url).netloc.replace('www.', '').split('.')[0].title()
        return self._create_result(title, date_str, content, url, source_name)
    
    def _create_result(self, title, date_str, content, url, source):
        """创建结果字典"""
        date_parsed = self.parse_date(date_str) if date_str else None
        
        return {
            'title': title,
            'date_str': date_str,
            'date_parsed': date_parsed,
            'content': content,
            'url': url,
            'source': source
        }
    
    def categorize_news(self, result):
        """自动分类新闻"""
        content = (result.get('title', '') + ' ' + result.get('content', '')).lower()
        
        categories = {
            'ai': ['ai', 'artificial intelligence', 'machine learning'],
            'higher': ['university', 'college', 'higher ed', 'enrollment', 'phd', 'graduate'],
            'teacher': ['teacher', 'educator', 'faculty', 'shortage'],
            'international': ['international student', 'visa', 'f-1', 'opt', 'foreign'],
            'federal': ['federal', 'congress', 'department of education', 'white house', 'trump'],
            'k12': ['k-12', 'elementary', 'secondary', 'school district'],
        }
        
        for cat, keywords in categories.items():
            if any(kw in content for kw in keywords):
                return cat
        return 'general'
    
    async def run_crawl(self, target_count=15):
        """运行爬虫"""
        print("="*70)
        print("🚀 高级教育新闻爬虫 - Playwright模式")
        print("="*70)
        
        # 加载来源配置
        with open(self.sources_file, 'r') as f:
            config = json.load(f)
        
        # 收集所有来源
        all_sources = []
        for cat_name, cat_data in config['categories'].items():
            for source in cat_data.get('sources', []):
                all_sources.append(source)
        
        # 按优先级排序
        all_sources.sort(key=lambda x: x.get('priority', 99))
        
        # 选择前20个高优先级来源
        selected_sources = all_sources[:20]
        
        print(f"\n📚 计划爬取 {len(selected_sources)} 个来源")
        print(f"🎯 目标: {target_count} 条新闻\n")
        
        fetched_count = 0
        
        for i, source in enumerate(selected_sources, 1):
            if fetched_count >= target_count:
                break
            
            print(f"[{i}/{len(selected_sources)}] 📡 {source['name']}")
            
            # 检查URL是否已存在
            if self.url_exists(source['url']):
                print(f"      ⏭️ 已存在，跳过")
                continue
            
            # 使用Playwright爬取
            result = await self.crawl_with_playwright(source['url'], source)
            
            if not result:
                print(f"      ❌ 爬取失败")
                continue
            
            # 检查日期
            if not self.is_recent_date(result.get('date_parsed'), days=7):
                print(f"      ⏭️ 日期不符: {result.get('date_str', 'N/A')}")
                continue
            
            # 检查标题和内容
            if not result.get('title') or not result.get('content'):
                print(f"      ⚠️ 数据不完整")
                continue
            
            # 添加到结果
            news_item = {
                'category': self.categorize_news(result),
                'title': result['title'],
                'source': result['source'],
                'original_date': result['date_str'],
                'summary': result['content'][:400] + '...' if len(result['content']) > 400 else result['content'],
                'url': result['url'],
                'fetched_from': 'local_source',
                'fetched_at': datetime.now().isoformat()
            }
            
            self.results.append(news_item)
            self.add_to_history(news_item)
            fetched_count += 1
            
            print(f"      ✅ 获取: {result['title'][:50]}...")
            print(f"         📅 {result['date_str']}")
            
            # 随机等待，避免被封
            await asyncio.sleep(random.uniform(3, 8))
        
        # 保存历史
        self.save_history()
        
        print(f"\n✅ 爬取完成！获取 {fetched_count} 条新闻")
        return fetched_count
    
    def generate_output(self):
        """生成输出文件"""
        output = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'Open Claw Advanced Crawler (Playwright)',
            'total_news': len(self.results),
            'news': self.results
        }
        
        # 使用相对路径
        output_file = os.path.join(self.project_dir, 'data', f'{output["date"]}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 输出文件: {output_file}")
        return output_file


async def main():
    """主函数"""
    crawler = AdvancedEducationCrawler()
    await crawler.run_crawl(target_count=15)
    crawler.generate_output()


if __name__ == '__main__':
    # 检查playwright是否安装
    try:
        import playwright
        print("✅ Playwright已安装")
    except ImportError:
        print("❌ 需要安装Playwright: pip install playwright")
        print("   然后运行: playwright install chromium")
        exit(1)
    
    asyncio.run(main())
