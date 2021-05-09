"""
1.等于号会不会出现在变量中？
"""

import pandas as pd
from logparser.utils.logdata import *

sign = '='
if __name__ == '__main__':
    result_dict = {
        'eventId': [],
        'content': [],
        'template': [],
    }
    for dataset in DATASET:
        print(dataset)
        if dataset != DATASET.Android:
            continue
        df = pd.read_csv(path_structured(dataset))
        # 去重
        # df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)
        for idx, row in df.iterrows():
            content = row['Content']
            eventId = row['EventId']
            template = row['EventTemplate']
            if content.find(sign) != -1:
                result_dict['eventId'].append(eventId)
                result_dict['content'].append(content)
                result_dict['template'].append(template)
    # save
    pd.DataFrame(result_dict).to_csv('sign_equal.csv')
