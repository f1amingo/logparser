"""
"""
import collections
import re

from logparser.utils.dataset import *
import pandas as pd

BLACK_LIST = collections.defaultdict(set)
BLACK_LIST[DATASET.OpenSSH] = {'sshd', 'root'}
BLACK_LIST[DATASET.Linux] = {'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Jun', 'Jul'}
BLACK_LIST[DATASET.Android] = {'null', 'android'}
BLACK_LIST[DATASET.Proxifier] = {'sec', 'KB', 'MB'}


def simplify_content(content: str) -> str:
    # 逗号换成空格
    content = re.sub(',', ' ', content)
    # 替换掉等号右边
    content = re.sub('=\S+\s?', ' ', content)
    # 包名
    content = re.sub('(\w+\.){2,}\w*', ' ', content)
    # 替换掉所有数字
    content = re.sub('\d+', '<*>', content)
    # 替换所有路径、地址
    content = re.sub('\S*/\S*', '<*>', content)
    # 替换掉<*>
    content = re.sub('\S*<\*>\S*', ' ', content)
    return content


def get_token_list(dataset: DATASET) -> list:
    token_counter = collections.defaultdict(int)
    df = pd.read_csv(log_path_structured(dataset))
    for idx, row in df.iterrows():
        content = row['Content']
        if dataset in {DATASET.OpenSSH, DATASET.Linux}:
            # 替换掉 "user <*>"
            content = re.sub('user\s\S+\s?', ' ', content)
        if dataset in {DATASET.OpenSSH}:
            content = re.sub('for\s\S+\s', ' ', content)
        if dataset in {DATASET.Android}:
            content = re.sub('".*"', ' ', content)
        # if dataset in {DATASET.Proxifier}:
        #     content = re.sub('\(.*?\)', ' ', content)

        content = simplify_content(content)
        content_token_list = re.split('\W+', content)
        for token in content_token_list:
            if re.fullmatch('([a-zA-Z*.-]{2,})', token):
                token_counter[token] += 1
    black_list = BLACK_LIST[dataset]
    # token_list = [t for t in token_counter if token_counter[t] > 1 and t not in black_list]
    token_list = [t for t in token_counter if t not in black_list]
    token_list.append('SPP.')  # Windows
    token_list.append('NODEVssh')  # Linux
    return token_list


if __name__ == '__main__':
    res = get_token_list(DATASET.Android)
    print(res)

    # result_dict = collections.defaultdict(list)
    # for dataset in DATASET:
    #     print(dataset.value)
    #     if dataset != DATASET.Android:
    #         continue
    #     df = pd.read_csv(log_path_structured(dataset))
    #     df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)
    #     for idx, row in df.iterrows():
    #         eventId = row['EventId']
    #         content = row['Content']
    #         template = row['EventTemplate']
    #         simple_content = simplify_content(content)
    #         result_dict['EventId'].append(eventId)
    #         result_dict['SimpleContent'].append(' '.join(simple_content.split()))
    #         result_dict['EventTemplate'].append(template)
    #         result_dict['Content'].append(content)
    #
    # pd.DataFrame(result_dict).to_csv('%s.csv' % os.path.basename(__file__), index=False)
