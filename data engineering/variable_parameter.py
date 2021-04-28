"""
1. 变长变量的具体情况
2. 哪些模板含有变长变量
3. 变长变量的数量，对结果影响有多大

变长变量位置一定是靠后的
变长变量是一种普遍的现象，但影响大就只有几个

HDFS
{'E4': 3})
Hadoop
{})
Spark
{'E2': 112, 'E3': 37})
Zookeeper
{'E44': 3})
BGL
{'E73': 5, 'E109': 1, 'E65': 1})
HPC
{'E43': 4, 'E20': 2})
Thunderbird
{'E111': 10, 'E4': 1, 'E9': 2, 'E146': 34, 'E147': 1})
Windows
{'E13': 6})
Linux
{'E29': 909, 'E112': 1, 'E68': 1})
Andriod
{'E10': 1, 'E131': 4, 'E108': 1, 'E41': 25})
Apache
{})
HealthApp
{})
Proxifier
{'E8': 947})
OpenSSH
{'E14': 2})
OpenStack
{'E25': 931, 'E26': 64, 'E24': 22})
Mac
{'E48': 14, 'E130': 7, 'E331': 12, 'E210': 4, 'E204': 6, 'E154': 3, 'E265': 1, 'E107': 1, 'E30': 1, 'E88': 1})
"""

from logs.logdata import *
import pandas as pd
import collections

template_list = []
content_list = []
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
        template_split = template.split()
        content_split = content.split()
        if eventId in len_dict:
            len_d = len_dict[eventId]
            if len_d is None or len_d != len(content_split):
                len_dict[eventId] = None
                counter[eventId] += 1
                template_list.append(template)
                content_list.append(content_split)
                eventId_list.append(eventId)
                dataset_list.append(dataset.value)
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
out_df['eventId'] = eventId_list
out_df['template'] = template_list
out_df['content'] = content_list
out_df.to_csv('variable.csv')
