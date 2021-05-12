from logparser.utils.dataset import *
import pandas as pd

df = pd.read_csv(log_path_template(DATASET.HDFS))
result = []
for idx, row in df.iterrows():
    template = row['EventTemplate']
    eventId = row['EventId']
    split_list = template.log_split()
    para_count = 0
    for token in split_list:
        if token.find('<*>') > -1:
            para_count += 1
    result.append((len(split_list), para_count))

result.sort()
print(result)
