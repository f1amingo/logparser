import collections
import pandas as pd
from logs.logdata import *
from logparser.ADC.log_signature import calc_signature

# 读入数据
df = pd.read_csv(path_structured(DATASET.Linux))
# 可能不存在
df.drop(['Date', 'Time', 'Pid', 'Level', 'Component'], axis=1, inplace=True, errors='ignore')
# 每个类型只保留一条
df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)

sig_bins = collections.defaultdict(list)
sig_list = []
eventId_list = []
content_list = []
template_list = []
# 解析每一行
for idx, row in df.iterrows():
    this_signature = calc_signature(row['Content'])
    sig_bins[this_signature].append(row['EventId'])
    sig_list.append(this_signature)
    eventId_list.append(row['EventId'])
    content_list.append(row['Content'])
    template_list.append(row['EventTemplate'])

print(sig_bins)
print(len(sig_bins))
out_dict = {}
out_dict['signature'] = sig_list
# out_dict['eventId'] = eventId_list
out_dict['content'] = content_list
out_dict['template'] = template_list
out_df = pd.DataFrame(out_dict)
out_df.to_csv('./test.csv', index=False)

# result_details = [df[df['EventId'].isin(result[sig])]['Content'].tolist() for sig in result]
# result_more_than_ten = [template_list for template_list in result_details if len(template_list) > 10]
# df.sort_values('EventId').to_csv('./test.csv')
