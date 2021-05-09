"""
如何评价log的相似度
1. Jaccard距离没有顺序信息，不太合适
2. 需要考虑顺序
3. 针对变长变量，效果如何
4. 针对模板包含问题，效果如何
"""

import re

import pandas as pd
from logparser.utils.logdata import *

DELIMITERS = '[ =|,:]'


# 前向、后向
def log_sim(log1: str, log2: str) -> (float, float):
    split_list1, split_list2 = re.split(DELIMITERS, log1), re.split(DELIMITERS, log2)
    m, n = len(split_list1), len(split_list2)
    if m > n:
        # 让log1更短
        split_list1, split_list2 = split_list2, split_list1
        m, n = n, m
    i, j = 0, 0
    forward, backward = 0, 0
    while i < m:
        forward += 1 if split_list1[i] != '' and split_list1[i] == split_list2[j] else 0
        i += 1
        j += 1
        backward += 1 if split_list1[-i] != '' and split_list1[-i] == split_list2[-j] else 0
    return forward / m, backward / m


# def log_sim(log1: str, log2: str) -> (float, float):
#     # split_list1, split_list2 = log1.split(), log2.split()
#     split_list1, split_list2 = re.split(DELIMITERS, log1), re.split(DELIMITERS, log2)
#     m, n = len(split_list1), len(split_list2)
#     if m > n:
#         # 让log1更短
#         split_list1, split_list2 = split_list2, split_list1
#         m, n = n, m
#     i, j = 0, 0
#     k = 0
#     while i < m:
#         k += 1 if split_list1[i] == split_list2[j] else 0
#         i += 1
#         j += 1
#     return k / m, 0


if __name__ == '__main__':
    a = "ready=true,policy=3,wakefulness=1,wksummary=0x23,uasummary=0x1,bootcompleted=true,boostinprogress=false,waitmodeenable=false,mode=false,manual=38,auto=-1,adj=0.0userId=0"
    b = "ready=true,policy=<*>,wakefulness=<*>,wksummary=<*>,uasummary=<*>,bootcompleted=true,boostinprogress=false,waitmodeenable=false,mode=false,manual=<*>,auto=<*>,adj=<*>.0userId=<*>"
    print(log_sim(a, b))

    result_dict = {
        'dataset': [],
        'eventId': [],
        'log_sim': [],
        'content': [],
        'template': [],
    }

    for dataset in DATASET:
        print(dataset)
        if dataset != DATASET.Android:
            continue
        df = pd.read_csv(path_structured(dataset))
        for idx, row in df.iterrows():
            content = row['Content']
            eventId = row['EventId']
            template = row['EventTemplate']
            # fo, ba = log_sim(content, template)
            fo, ba = log_sim(content, template)
            if fo < 0.5 and ba < 0.5:
                result_dict['dataset'].append(dataset)
                result_dict['eventId'].append(eventId)
                result_dict['log_sim'].append((fo, ba))
                result_dict['content'].append(content)
                result_dict['template'].append(template)
                # result_dict['content'].append(re.split(DELIMITERS, content))
                # result_dict['template'].append(re.split(DELIMITERS, template))

    pd.DataFrame(result_dict).to_csv('log_similarity.csv')
