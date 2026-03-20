#!/usr/bin/env python3
"""
双源教育新闻抓取器
结合 Tavily 搜索 + 本地来源库，每日生成25条新闻
结构：10条(Tavily新发现) + 15条(本地来源库)
"""
import os
import sys
import json
from datetime import datetime, timedelta
from crawler_engine import EducationNewsCrawler

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DualSourceNewsFetcher:
    """双源新闻抓取器"""
    
    def __init__(self, target_date=None):
        self.target_date = target_date or datetime.now()
        self.crawler = EducationNewsCrawler()
        
        # 使用相对路径（适配GitHub Actions）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        
        self.sources_file = os.path.join(project_dir, 'sources', 'index.json')
        self.history_file = os.path.join(project_dir, 'history', 'news_history.json')
        
        with open(self.sources_file, 'r') as f:
            self.sources_config = json.load(f)
        
        self.load_history()
        
        # 结果池
        self.tavily_pool = []
        self.local_pool = []
        self.all_news = []
    
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
    
    def is_url_new(self, url):
        """检查URL是否为新"""
        return url not in self.history.get('url_index', {})
    
    def add_to_history(self, entry):
        """添加到历史"""
        if self.is_url_new(entry['url']):
            self.history['entries'].append(entry)
            self.history['url_index'][entry['url']] = len(self.history['entries']) - 1
            self.history['total_entries'] = len(self.history['entries'])
            return True
        return False
    
    def check_date_in_range(self, date_obj, days=7):
        """检查日期是否在目标范围内"""
        if not date_obj:
            return False
        today = datetime.now()
        delta = (today - date_obj).days
        return 0 <= delta <= days
    
    def fetch_from_local_sources(self, max_items=20):
        """从本地来源库抓取"""
        print("🔍 开始扫描本地来源库...")
        
        all_sources = []
        for category, data in self.sources_config.get('categories', {}).items():
            for source in data.get('sources', []):
                all_sources.append(source)
        
        # 按优先级排序
        all_sources.sort(key=lambda x: x.get('priority', 99))
        
        fetched_count = 0
        for source in all_sources[:30]:  # 先扫描前30个优先来源
            if fetched_count >= max_items:
                break
            
            try:
                print(f"  📡 扫描: {source['name']}")
                
                # 使用爬虫获取该来源的最新文章
                result = self.crawler.crawl_by_source(
                    source['url'], 
                    source.get('crawler', 'generic'),
                    source['name']
                )
                
                if not result:
                    continue
                
                # 检查日期
                if not self.check_date_in_range(result.get('date_parsed')):
                    print(f"    ⏭️ 日期不符，跳过")
                    continue
                
                # 检查是否已存在
                if not self.is_url_new(result['url']):
                    print(f"    ⏭️ 已存在，跳过")
                    continue
                
                # 添加到本地池
                news_item = {
                    'category': self.categorize_news(result),
                    'title': result['title'],
                    'source': source['name'],
                    'original_date': result['date_str'],
                    'summary': self.generate_summary(result.get('content', '')),
                    'url': result['url'],
                    'fetched_from': 'local_source',
                    'fetched_at': datetime.now().isoformat()
                }
                
                self.local_pool.append(news_item)
                self.add_to_history(news_item)
                fetched_count += 1
                print(f"    ✅ 获取: {result['title'][:50]}...")
                
            except Exception as e:
                print(f"    ❌ 错误: {e}")
                continue
        
        print(f"✅ 本地来源库扫描完成，获取 {fetched_count} 条")
        return fetched_count
    
    def fetch_from_tavily(self, max_items=15):
        """从Tavily搜索获取"""
        print("🔍 开始Tavily搜索...")
        
        try:
            from tavily import TavilyClient
            
            # 从环境变量获取API key
            api_key = os.getenv('TAVILY_API_KEY')
            if not api_key:
                print("❌ TAVILY_API_KEY 未设置")
                return 0
            
            client = TavilyClient(api_key=api_key)
            
            # 搜索查询
            queries = [
                "US education policy federal March 2026",
                "AI education schools policy 2026",
                "teacher shortage university enrollment 2026",
                "international student visa F1 2026",
                "higher education budget cuts 2026"
            ]
            
            fetched_count = 0
            new_sources = []
            
            for query in queries:
                if fetched_count >= max_items:
                    break
                
                print(f"  🔎 搜索: {query}")
                
                try:
                    response = client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=5
                    )
                    
                    for result in response.get('results', []):
                        if fetched_count >= max_items:
                            break
                        
                        url = result.get('url', '')
                        
                        # 跳过非教育类网站
                        if not self.is_education_related(url):
                            continue
                        
                        # 检查是否已存在
                        if not self.is_url_new(url):
                            continue
                        
                        # 爬取详细内容
                        crawled = self.crawler.crawl_generic(url)
                        if not crawled:
                            continue
                        
                        # 检查日期
                        if not self.check_date_in_range(crawled.get('date_parsed')):
                            continue
                        
                        # 检查是否为新来源
                        source_domain = self.extract_domain(url)
                        if not self.is_known_source(source_domain):
                            new_sources.append({
                                'url': url,
                                'domain': source_domain,
                                'title': result.get('title', '')
                            })
                        
                        # 添加到Tavily池
                        news_item = {
                            'category': self.categorize_news(crawled),
                            'title': crawled['title'] or result.get('title', ''),
                            'source': self.extract_source_name(url),
                            'original_date': crawled['date_str'],
                            'summary': self.generate_summary(result.get('content', '')),
                            'url': url,
                            'fetched_from': 'tavily',
                            'fetched_at': datetime.now().isoformat()
                        }
                        
                        self.tavily_pool.append(news_item)
                        self.add_to_history(news_item)
                        fetched_count += 1
                        
                except Exception as e:
                    print(f"    ❌ 搜索错误: {e}")
                    continue
            
            # 报告新发现来源
            if new_sources:
                print(f"\n📌 发现 {len(new_sources)} 个新来源:")
                for src in new_sources[:5]:
                    print(f"  • {src['domain']}")
            
            print(f"✅ Tavily搜索完成，获取 {fetched_count} 条")
            return fetched_count
            
        except ImportError:
            print("❌ 未安装 tavily 库")
            return 0
    
    def categorize_news(self, result):
        """自动分类新闻"""
        content = (result.get('title', '') + ' ' + result.get('content', '')).lower()
        
        if any(kw in content for kw in ['ai', 'artificial intelligence', 'machine learning']):
            return 'ai'
        elif any(kw in content for kw in ['university', 'college', 'higher ed', 'enrollment']):
            return 'higher'
        elif any(kw in content for kw in ['teacher', 'educator', 'faculty']):
            return 'teacher'
        elif any(kw in content for kw in ['international student', 'visa', 'f-1', 'opt']):
            return 'international'
        elif any(kw in content for kw in ['federal', 'congress', 'department of education', 'white house']):
            return 'federal'
        else:
            return 'general'
    
    def generate_summary(self, content, max_length=400):
        """生成中文摘要"""
        if not content:
            return "暂无内容"
        
        # 清理文本
        content = content.strip().replace('\n', ' ')
        
        # 截取前max_length字符
        if len(content) > max_length:
            summary = content[:max_length].rsplit(' ', 1)[0] + '...'
        else:
            summary = content
        
        return summary
    
    def is_education_related(self, url):
        """检查是否教育相关"""
        edu_keywords = [
            'education', 'university', 'college', 'school', 'teacher',
            'student', 'academic', 'edweek', 'chronicle', 'highered',
            'k12', 'learning', 'teaching', 'scholar'
        ]
        return any(kw in url.lower() for kw in edu_keywords)
    
    def extract_domain(self, url):
        """提取域名"""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def extract_source_name(self, url):
        """提取来源名称"""
        domain = self.extract_domain(url)
        return domain.replace('www.', '').split('.')[0].title()
    
    def is_known_source(self, domain):
        """检查是否已知来源"""
        for category, data in self.sources_config.get('categories', {}).items():
            for source in data.get('sources', []):
                if domain in source.get('url', ''):
                    return True
        return False
    
    def combine_and_select(self):
        """合并并精选25条新闻"""
        print("\n📊 开始合并精选...")
        
        # 目标：10条Tavily + 15条本地
        selected = []
        
        # 先选Tavily的（最多10条）
        tavily_selected = self.tavily_pool[:10]
        selected.extend(tavily_selected)
        print(f"  • Tavily来源: {len(tavily_selected)}条")
        
        # 再选本地来源的（补足到25条）
        remaining_slots = 25 - len(selected)
        local_selected = self.local_pool[:remaining_slots]
        selected.extend(local_selected)
        print(f"  • 本地来源: {len(local_selected)}条")
        
        # 去重（按URL）
        seen_urls = set()
        unique_selected = []
        for item in selected:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_selected.append(item)
        
        self.all_news = unique_selected
        print(f"✅ 最终精选: {len(unique_selected)}条 (目标: 25条)")
        
        return unique_selected
    
    def generate_output(self, output_file=None):
        """生成输出文件"""
        if not output_file:
            date_str = self.target_date.strftime('%Y-%m-%d')
            # 使用相对路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            output_file = os.path.join(project_dir, 'data', f'{date_str}.json')
        
        output = {
            'date': self.target_date.strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'Open Claw Dual-Source System',
            'source_method': 'Tavily(10) + Local Sources(15)',
            'total_news': len(self.all_news),
            'categories': self.count_categories(),
            'news': self.all_news
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 输出文件已生成: {output_file}")
        return output_file
    
    def count_categories(self):
        """统计分类数量"""
        counts = {}
        for item in self.all_news:
            cat = item.get('category', 'other')
            counts[cat] = counts.get(cat, 0) + 1
        return counts
    
    def run(self):
        """运行完整流程"""
        print("="*60)
        print(f"🚀 双源教育新闻抓取器启动")
        print(f"📅 目标日期: {self.target_date.strftime('%Y-%m-%d')}")
        print("="*60)
        
        # 1. 从本地来源库抓取
        self.fetch_from_local_sources(max_items=20)
        
        # 2. 从Tavily抓取
        self.fetch_from_tavily(max_items=15)
        
        # 3. 合并精选
        self.combine_and_select()
        
        # 4. 保存历史
        self.save_history()
        
        # 5. 生成输出
        output_file = self.generate_output()
        
        print("\n" + "="*60)
        print("✅ 所有任务完成!")
        print(f"📄 输出文件: {output_file}")
        print(f"📊 历史库总数: {len(self.history.get('entries', []))}条")
        print("="*60)


if __name__ == '__main__':
    fetcher = DualSourceNewsFetcher()
    fetcher.run()
