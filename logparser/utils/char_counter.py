import pandas as pd
import collections


# 对特殊符号进行统计
def count_mark(csv_file_path):
    df = pd.read_csv(csv_file_path)
    counter = collections.defaultdict(int)
    for idx, row in df.iterrows():
        row_content = row['Content']
        for ch in row_content:
            if not ch.isalnum():
                counter[ch] += 1
    return counter


if __name__ == '__main__':
    # res = count_mark('../../logs/Linux/Linux_2k.log_structured.csv')
    res = count_mark('../../logs/OpenStack/OpenStack_2k.log_structured.csv')
    print(res)
