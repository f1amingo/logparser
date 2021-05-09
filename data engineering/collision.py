"""
分析签名算法的碰撞程度
1. 每个桶的模板数目：最多、最少、平均、方差
"""

import pandas as pd
import numpy as np
from logparser.utils.logdata import *
import collections
from logparser.ADC.log_signature import calc_signature


class BinEntry:
    def __init__(self):
        self.sig = None
        self.templates = []


if __name__ == '__main__':
    result_dict = {
        'dataset': [],
        'template_count': [],
        'bin_count': [],
        'top1': [],
        'top2': [],
        'top3': [],
        'mean': [],
        'std': [],
        'min': [],
    }
    for dataset in DATASET:
        print(dataset)
        # if dataset != DATASET.Mac:
        #     continue
        df = pd.read_csv(path_structured(dataset))
        # df.drop(['Date', 'Time', 'Pid', 'Level', 'Component'], axis=1, inplace=True, errors='ignore')
        # 去重
        df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)
        bin_dict = collections.defaultdict(BinEntry)
        for idx, row in df.iterrows():
            content = row['Content']
            sig = calc_signature(content)
            bin_dict[sig].sig = sig
            bin_dict[sig].templates.append(content)
        count_list = [len(bin_dict[k].templates) for k in bin_dict]
        count_list.sort()
        result_dict['dataset'].append(dataset.value)
        result_dict['template_count'].append(len(df))
        result_dict['bin_count'].append(len(count_list))
        result_dict['min'].append(count_list[0])
        result_dict['top1'].append(count_list[-1])
        result_dict['top2'].append(count_list[-2])
        result_dict['top3'].append(count_list[-3])
        result_dict['mean'].append(np.mean(count_list))
        result_dict['std'].append(np.std(count_list))

pd.DataFrame(result_dict).to_csv('collision.csv')
