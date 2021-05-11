"""
分析签名算法的碰撞程度
1. 每个桶的模板数目：最多、最少、平均、方差
"""

import numpy as np
from logparser.utils.dataset import *
import collections
from logparser.ADC import log_signature, log_split


class BinEntry:
    def __init__(self):
        self.sig = None
        self.templates = []


if __name__ == '__main__':
    result_dict = collections.defaultdict(list)
    for dataset in DATASET:
        print(dataset)
        # if dataset != DATASET.Mac:
        #     continue
        df = pd.read_csv(log_path_structured(dataset))
        # df.drop(['Date', 'Time', 'Pid', 'Level', 'Component'], axis=1, inplace=True, errors='ignore')
        df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)
        bin_dict = collections.defaultdict(BinEntry)
        for idx, row in df.iterrows():
            log_content = row['Content']
            log_token_list = log_split(log_content)
            log_sig = log_signature(log_token_list)
            bin_dict[log_sig].sig = log_sig
            bin_dict[log_sig].templates.append(log_content)
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
        result_dict['medium'].append(count_list[len(count_list) // 2])
        result_dict['std'].append(np.std(count_list))

    pd.DataFrame(result_dict).to_csv('%s.csv' % os.path.basename(__file__), index=False)
