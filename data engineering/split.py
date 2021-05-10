"""
1. 如何才能将日志“完美切分”
2. 同类日志切分长度要一致

"." 一定不能使用
"""
import re
from logparser.utils.dataset import *
import pandas as pd

result_dict = {
    'dataset': [],
    'eventId': [],
    'content': [],
    'conflict': [],
}
for dataset in DATASET:
    print(dataset.value)
    if dataset == DATASET.Proxifier or dataset == DATASET.OpenStack:
        continue
    df = pd.read_csv(log_path_structured(dataset))
    len_dict = {}
    pre_dict = {}
    for idx, row in df.iterrows():
        eventId = row['EventId']
        content = row['Content']
        template = row['EventTemplate']
        content = re.sub('".*"', '<*>', content)
        # 替换连续空格
        # content = re.sub('\s+', ' ', content)
        content = re.sub('\(\)', '(null)', content)
        content_split = re.split('([\s=,:|()\[\]]+)', content)
        if eventId in len_dict:
            if len_dict[eventId] != len(content_split):
                result_dict['dataset'].append(dataset.value)
                result_dict['eventId'].append(eventId)
                result_dict['content'].append(content_split)
                result_dict['conflict'].append(pre_dict[eventId])
        else:
            len_dict[eventId] = len(content_split)
            pre_dict[eventId] = content_split

out_df = pd.DataFrame(result_dict)
out_df.to_csv('%s.csv' % os.path.basename(__file__), index=False)
