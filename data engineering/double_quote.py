"""
1.双引号带来了哪些问题？
2.双引号内的一定是变量吗？
3.如何解决

'Thunderbird': 2, 'Windows': 4, 'Android': 118, 'OpenStack': 1017, 'Mac': 63
Thunderbird total 2: 'E29'
Windows total 4: 'E10', 'E2'
Android total 118: 'E10', 'E11', 'E109', 'E108'
OpenStack total 1017: 'E24', 'E26', 'E25'
Mac total 63: 'E187', 'E286', 'E76', 'E85', 'E197', 'E26', 'E313', 'E304', 'E84', 'E107', 'E30', 'E285', 'E22', 'E311', 'E306', 'E83', 'E325', 'E303', 'E77', 'E191', 'E324', 'E190', 'E27', 'E245', 'E91', 'E80'

Thunderbird：yes
Windows：E10 yes; E2 no "(null)"
Android："PowerManagerService.WakeLocks" tag="<*>"
OpenStack："GET <*>"
Mac：
"""
import collections

import pandas as pd
from logparser.utils.logdata import *


# 得到双引号内的内容
# 包含双引号
def get_double_quote_content(content: str) -> [str]:
    pass


counter = collections.defaultdict(int)
eventIdList = collections.defaultdict(set)
with open('double_quote.txt', 'w') as f:
    for dataset in DATASET:
        f.write('\n\n' + dataset.value + '\n')
        df = pd.read_csv(path_structured(dataset))
        for idx, row in df.iterrows():
            content = row['Content']
            eventId = row['EventId']
            if content.find('"') != -1:
                eventIdList[dataset.value].add(eventId)
                counter[dataset.value] += 1
                f.write(content + '\n')
print(counter)
print(eventIdList)
