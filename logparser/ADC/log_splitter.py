from typing import List
import config

import pandas as pd
from collections import defaultdict


def bitmapToNumber(_bitmap: List):
    _res = 0
    for _digit in _bitmap:
        _digit = 1 if _digit else 0
        _res = 2 * _res + _digit
    return _res


this_dataset = config.DATASET.Android.value
CSV_FILE_PATH = 'C:/Users/think/Desktop/logparser/logs/%s/%s_2k.log_structured.csv' % (this_dataset, this_dataset)
df = pd.read_csv(CSV_FILE_PATH)
# 可能不存在
df.drop(['Date', 'Time', 'Pid', 'Level', 'Component'], axis=1, inplace=True, errors='ignore')
df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)
lookup = defaultdict(int)
for row in df.itertuples():
    for c in row.Content:
        if not c.isalnum():
            lookup[c] += 1
print(lookup)
# df.to_csv('./test.csv')

RULE_TABLE = {
    ' ': lambda t: ' ' in t,
    '_': lambda t: '_' in t,
    '*': lambda t: '*' in t,
    ':': lambda t: ':' in t,
    '/': lambda t: '/' in t,
    '(': lambda t: '(' in t,
    '{': lambda t: '{' in t,
    '[': lambda t: '[' in t,
    '.': lambda t: '.' in t,
    '=': lambda t: '=' in t,
    '-': lambda t: '-' in t,
    '+': lambda t: '+' in t,
    ',': lambda t: ',' in t,
    '\'': lambda t: '\'' in t,
    '"': lambda t: '"' in t,
    ';': lambda t: ';' in t,
    '?': lambda t: '?' in t,
    '!': lambda t: '!' in t,
    '$': lambda t: '$' in t,
    '<': lambda t: '<' in t,
    '>': lambda t: '>' in t,
    '@': lambda t: '@' in t,
    '|': lambda t: '|' in t,
    '#': lambda t: '#' in t,
    # 'ip': lambda t: re.match(r'(\d+\.){3}\d+(:\d+)?', t) is not None,
}

RULE_IDX = {}
for idx, sym in enumerate(RULE_TABLE):
    RULE_IDX[sym] = idx
bitmap = [0] * len(RULE_TABLE)
result = defaultdict(list)
for row in df.itertuples():
    this_bitmap = bitmap.copy()
    this_token_list = row.Content.split()
    for token in this_token_list:
        for idx, rule in enumerate(RULE_IDX):
            if this_bitmap[idx] == 0:
                is_match = RULE_TABLE[rule](token)
                this_bitmap[idx] = int(is_match)
    result[bitmapToNumber(this_bitmap)].append(row.EventId)
print(result)
df['EventId'].str.contains("E42")

f = ['E9', 'E15', 'E12', 'E8', 'E14', 'E13']
df[df['EventId'].isin(f)]['Content']
