import pandas as pd
import collections
from logparser.utils.dataset import *
import seaborn as sns
import matplotlib.pyplot as plt

dataset_list = []
top_list = []
last_list = []
for dataset in DATASET:
    df = pd.read_csv(log_path_structured(dataset))
    counter = collections.defaultdict(int)
    for idx, row in df.iterrows():
        split_list = row['Content'].log_split()
        for token in split_list:
            counter[token] += 1
    sorted_counter = dict(sorted(counter.items(), key=lambda item: -item[1]))
    # plot
    keys = [k for k in sorted_counter if sorted_counter[k] > 5]
    # keys = [k for k in sorted_counter]
    vals = [sorted_counter[k] for k in keys]
    sns_plot = sns.barplot(x=keys, y=vals)
    sns_plot.set(title=dataset)
    sns_plot.get_figure().savefig('./token-frequency/%s.png' % dataset.value)
    plt.title(dataset)
    plt.show()
    # top3 last3
    counter_list = list(sorted_counter)
    a, b, c = counter_list[0], counter_list[1], counter_list[2]
    x, y, z = counter_list[-1], counter_list[-2], counter_list[-3]
    top_list.append([(a, counter[a]), (b, counter[b]), (c, counter[c]), ])
    last_list.append([(x, counter[x]), (y, counter[y]), (z, counter[z]), ])
    dataset_list.append(dataset.value)
    print('%s finished.' % dataset)

df = pd.DataFrame()
df['Dataset'] = dataset_list
df['Top'] = top_list
df['Last'] = last_list
df.to_csv('./token-frequency/frequency.csv')
