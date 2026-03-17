#!/usr/bin/env python3
"""
Fetch education news from various sources and generate daily JSON file.
"""
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# Categories and their keywords
CATEGORIES = {
    'federal': ['federal', 'department of education', 'white house', 'congress', 'legislation'],
    'ai': ['artificial intelligence', 'AI education', 'AI literacy', 'chatbot', 'machine learning'],
    'higher': ['higher education', 'university', 'college', 'tuition', 'enrollment', 'accreditation'],
    'teacher': ['teacher shortage', 'educator', 'faculty', 'professor', 'teaching'],
    'international': ['international student', 'F-1 visa', 'study abroad', 'foreign student'],
    'stem': ['STEM', 'science education', 'math education', 'engineering education'],
    'k12': ['K-12', 'elementary', 'secondary', 'high school', 'middle school']
}

# Midwest states
MIDWEST_STATES = ['Illinois', 'Indiana', 'Iowa', 'Michigan', 'Missouri', 
                  'Minnesota', 'Kansas', 'Wisconsin', 'Nebraska', 
                  'South Dakota', 'North Dakota', 
                  'IL', 'IN', 'IA', 'MI', 'MO', 'MN', 'KS', 'WI', 'NE', 'SD', 'ND']

def categorize_news(title, content):
    """Categorize news based on keywords."""
    text = (title + ' ' + content).lower()
    
    for category, keywords in CATEGORIES.items():
        if any(keyword.lower() in text for keyword in keywords):
            return category
    
    return 'other'

def is_midwest_related(text):
    """Check if news is related to Midwest states."""
    return any(state in text for state in MIDWEST_STATES)

def generate_sample_news(date_str):
    """Generate sample news for demonstration."""
    # This is a placeholder - in production, this would fetch from real APIs
    return {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "generated_by": "Open Claw",
        "total_news": 10,
        "categories": {
            "federal": 2,
            "higher": 3,
            "ai": 2,
            "teacher": 1,
            "international": 1,
            "stem": 1
        },
        "news": [
            {
                "category": "federal",
                "title": f"美国教育部动态更新 - {date_str}",
                "source": "US Department of Education",
                "summary": "联邦教育政策最新动态...",
                "content": "详细的联邦教育政策内容...",
                "url": "https://www.ed.gov",
                "timestamp": f"{date_str}T08:00:00Z"
            }
            # ... more news items would be here
        ]
    }

def main():
    """Main function to fetch and save news."""
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create data directory if not exists
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Generate news data
    news_data = generate_sample_news(today)
    
    # Save to file
    output_file = data_dir / f"{today}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ News data saved to {output_file}")
    print(f"📊 Total news items: {news_data['total_news']}")

if __name__ == '__main__':
    main()
