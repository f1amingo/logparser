# 在签名为0的桶内，测试倒排索引可行性
import collections
import pandas as pd
from logparser.utils.logdata import *

zero_index = ['E101', 'E37', 'E38', 'E90', 'E88', 'E61', 'E75', 'E106', 'E2', 'E3', 'E118', 'E65', 'E58', 'E42',
              'E4', 'E117', 'E24', 'E69', 'E52', 'E85', 'E40', 'E114', 'E113', 'E93', 'E25', 'E96', 'E46', 'E26', 'E92',
              'E56', 'E57', 'E44', 'E45', 'E86', 'E67', 'E63', 'E48', 'E49', 'E94', 'E95', 'E53', 'E87', 'E66']

# 读入数据
df = pd.read_csv(path_structured(DATASET.Linux))
# 可能不存在
df.drop(['LineId', 'Date', 'Time', 'Month', 'PID', 'Level', 'Component', 'EventTemplate', 'EventId'], axis=1,
        inplace=True,
        errors='ignore')
# 每个类型只保留一条
df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)
zero_df = df[df['EventId'].isin(zero_index)]

result = collections.defaultdict(list)

inverted_index = collections.defaultdict(list)  # token到模板id列表
template_dict = []  # id到模板
for idx, row in zero_df.iterrows():
    index_score = [0] * len(template_dict)
    split_list = row['Content'].split()
    max_score = 0
    max_idx = -1
    for token in split_list:
        if token in inverted_index:
            for id in inverted_index[token]:
                index_score[id] += 1
                if index_score[id] > max_score:
                    max_score = index_score[id]
                    max_idx = id
    # 匹配
    if (len(split_list) == 1 and max_score == 1) or max_score >= 2:
        # result[row['EventId']] = max_idx
        result[max_idx].append(row['EventId'])
    else:
        this_idx = len(template_dict)
        template_dict.append(row['Content'])
        for token in split_list:
            if token in inverted_index:
                inverted_index[token].append(this_idx)
            else:
                inverted_index[token] = [this_idx]

        result[this_idx].append(row['EventId'])

zero_df.to_csv('./zero.csv', index=False)
