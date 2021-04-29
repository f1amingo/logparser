"""
1. 变长变量的具体情况
2. 哪些模板含有变长变量
3. 变长变量的数量，对结果影响有多大

变长变量位置一定是靠后的
变长变量是一种普遍的现象，但影响大就只有几个
只管Thunderbird、Android就好，最小长度为7

HDFS 4条
Zookeeper 10条
HPC 7条
Thunderbird 23条
Andriod 77条
特殊情况：E10 tag="View Lock"
Mac 7条

HDFS
defaultdict(<class 'int'>, {'E4': 3})
Hadoop
defaultdict(<class 'int'>, {})
Spark
defaultdict(<class 'int'>, {})
Zookeeper
defaultdict(<class 'int'>, {'E44': 9})
BGL
defaultdict(<class 'int'>, {})
HPC
defaultdict(<class 'int'>, {'E43': 3, 'E20': 2})
Thunderbird
defaultdict(<class 'int'>, {'E146': 19, 'E111': 2})
Windows
defaultdict(<class 'int'>, {})
Linux
defaultdict(<class 'int'>, {})
Andriod
defaultdict(<class 'int'>, {'E108': 25, 'E41': 24, 'E10': 25})
HealthApp
defaultdict(<class 'int'>, {})
OpenSSH
defaultdict(<class 'int'>, {})
Mac
defaultdict(<class 'int'>, {'E265': 2, 'E210': 3})
"""

from logs.logdata import *
import pandas as pd
import collections
import shlex

template_list = []
content_list = []
message_length = []
eventId_list = []
dataset_list = []
for dataset in DATASET:
    print(dataset.value)
    df = pd.read_csv(path_structured(dataset))
    counter = collections.defaultdict(int)
    len_dict = {}
    for idx, row in df.iterrows():
        eventId = row['EventId']
        content = row['Content']
        template = row['EventTemplate']
        # template_split = template.split()
        content_split = content.split()
        # content_split = shlex.split(content)
        if eventId in len_dict:
            len_d = len_dict[eventId]
            if len_d is None or len_d != len(content_split):
                len_dict[eventId] = None
                counter[eventId] += 1
                template_list.append(template)
                content_list.append(content_split)
                eventId_list.append(eventId)
                dataset_list.append(dataset.value)
                message_length.append(len(content_split))
        else:
            len_dict[eventId] = len(content_split)

        # if len(template_split) != len(content_split):
        #     counter[eventId] += 1
        #     template_list.append(template)
        #     content_list.append(content_split)
        #     eventId_list.append(eventId)
        #     dataset_list.append(dataset.value)
    print(counter)

out_df = pd.DataFrame()
out_df['dataset'] = dataset_list
out_df['length'] = message_length
out_df['eventId'] = eventId_list
out_df['content'] = content_list
out_df['template'] = template_list
out_df.to_csv('variable.csv', index=False)
