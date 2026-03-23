#!/usr/bin/env python3
import json
import glob
import os
import datetime

data_files = glob.glob('data/2026-*.json')
dates = sorted([os.path.basename(f).replace('.json', '') for f in data_files], reverse=True)

with open('data/index.json', 'r') as f:
    idx = json.load(f)

idx['dates'] = dates
idx['total_days'] = len(dates)
idx['last_updated'] = datetime.datetime.now().isoformat()

with open('data/index.json', 'w') as f:
    json.dump(idx, f, indent=2, ensure_ascii=False)

print(f'Updated index: {dates}')
