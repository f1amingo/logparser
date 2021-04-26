"""
1.如果消息长度为1，会有变量吗？
2.消息长度为2呢？3呢？
3.消息长度为多少时，开始有变量。

长度为1并且含有变量：
BGL E65: fpr29=<*> 1次
HPC E2: ambient=<*> 200+次
Andriod E29: cancelNotification,index:<*> 23次
Andriod E32: cancelNotificationLocked:<*>|<*>|<*>|null|<*> 2次
Andriod E103: ready=true,policy=<*>,wakefulness=<*>,wksummary=<*>,uasummary=<*>,... 199次
Andriod E111: removeNotification:<*>|<*>|<*>|null|<*> 2次
Mac E249: IOHibernatePollerOpen(<*>) 2次
Mac E255: kern_open_file_for_direct_io(<*>) 1次

需要增加分隔符
"""
import re

import pandas as pd
from logs.logdata import *

if __name__ == '__main__':
    for dataset in DATASET:
        df = pd.read_csv(path_template(dataset))
        # for idx, row in df.iterrows():
        #     template = row['EventTemplate']
        #     if template.find('<*>') == -1:
        #         split_list = template.split()
        #         print(str(len(split_list)) + ': ' + template)
        for idx, row in df.iterrows():
            template = row['EventTemplate']
            eventId = row['EventId']
            # split_list = template.split()
            split_list = re.split('[ =|,]', template)
            if len(split_list) == 1:
                if template.find('<*>') == -1:
                    print('%s %s: %s' % (dataset.value, eventId, template))
