"""
如何评价log的相似度
1. Jaccard距离没有顺序信息，不太合适
2. 需要考虑顺序
3. 针对变长变量，效果如何
4. 针对模板包含问题，效果如何
"""

import re

import pandas as pd
from logparser.utils.dataset import *

DELIMITERS = {' ', '=', ',', ':', '|', '(', ')', '[', ']'}
# DELIMITERS = {' ', '=', ',', '|', '(', ')', '[', ']'}
SPLIT_DELIMITER = '([' + ''.join(['\\' + k for k in DELIMITERS]) + '])'


def log_sim(token_list1: list, token_list2: list) -> (float, float):
    m, n = len(token_list1), len(token_list2)
    if m != n:
        return 0, 0
    # 利用前缀信息
    # for i in range(min(self.pre, n)):
    #     if token_list1[i] != token_list2[i]:
    #         return 0, 0
    count = 0
    for i in range(n):
        if token_list1[i] == '<*>' or token_list1[i] == token_list2[i]:
            count += 1
        # isDel1 = token_list1[i] in DELIMITERS
        # isDel2 = token_list2[i] in DELIMITERS
        # if (not isDel1 and not isDel2) or (isDel1 and isDel2):
        #     if token_list1[i] == '<*>' or token_list1[i] == token_list2[i]:
        #         count += 1
        # else:
        #     return 0, 0
    return count / m, 0


if __name__ == '__main__':
    a = "ready=true,policy=3,wakefulness=1,wksummary=0x23,uasummary=0x1,bootcompleted=true,boostinprogress=false,waitmodeenable=false,mode=false,manual=38,auto=-1,adj=0.0userId=0"
    b = "ready=true,policy=<*>,wakefulness=<*>,wksummary=<*>,uasummary=<*>,bootcompleted=true,boostinprogress=false,waitmodeenable=false,mode=false,manual=<*>,auto=<*>,adj=<*>.0userId=<*>"
    # print(log_sim(a, b))

    result_dict = {
        'dataset': [],
        'eventId': [],
        'log_sim': [],
        'content': [],
        'template': [],
    }

    for dataset in DATASET:
        print(dataset)
        # if dataset != DATASET.Android:
        #     continue
        df = pd.read_csv(log_path_structured(dataset))
        for idx, row in df.iterrows():
            content = row['Content']
            eventId = row['EventId']
            template = row['EventTemplate']
            content_token_list = re.split(SPLIT_DELIMITER, content)
            template_token_list = re.split(SPLIT_DELIMITER, template)
            score, _ = log_sim(template_token_list, content_token_list)
            if score < 0.5:
                result_dict['dataset'].append(dataset)
                result_dict['eventId'].append(eventId)
                result_dict['log_sim'].append((score, len(content_token_list), len(template_token_list)))
                result_dict['content'].append(content_token_list)
                result_dict['template'].append(template_token_list)

    pd.DataFrame(result_dict).to_csv('%s.csv' % os.path.basename(__file__), index=False)
