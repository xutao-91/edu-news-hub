#!/usr/bin/env python3
"""
Update the index.json file with all available dates.
"""
import json
from pathlib import Path
from datetime import datetime

def main():
    data_dir = Path('data')
    
    # Find all date JSON files
    date_files = sorted([f.stem for f in data_dir.glob('*.json') if f.stem != 'index'])
    
    # Load existing index
    index_file = data_dir / 'index.json'
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {}
    
    # Update index
    index['dates'] = date_files
    index['total_days'] = len(date_files)
    index['last_updated'] = datetime.now().isoformat()
    
    # Save index
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Index updated: {len(date_files)} days available")
    print(f"📅 Latest: {date_files[-1] if date_files else 'None'}")

if __name__ == '__main__':
    main()
