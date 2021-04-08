from typing import List
import config
import pandas as pd
import os
from collections import defaultdict
from logparser import evaluator


def LCS(seq1, seq2):
    lengths = [[0 for j in range(len(seq2) + 1)] for i in range(len(seq1) + 1)]
    # row 0 and column 0 are initialized to 0 already
    for i in range(len(seq1)):
        for j in range(len(seq2)):
            if seq1[i] == seq2[j]:
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

    # read the substring out from the matrix
    result = []
    lenOfSeq1, lenOfSeq2 = len(seq1), len(seq2)
    while lenOfSeq1 != 0 and lenOfSeq2 != 0:
        if lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1 - 1][lenOfSeq2]:
            lenOfSeq1 -= 1
        elif lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1][lenOfSeq2 - 1]:
            lenOfSeq2 -= 1
        else:
            assert seq1[lenOfSeq1 - 1] == seq2[lenOfSeq2 - 1]
            result.insert(0, seq1[lenOfSeq1 - 1])
            lenOfSeq1 -= 1
            lenOfSeq2 -= 1
    return result


class LCSObject:
    '''
        Class object to store a log group with the same template
    '''

    def __init__(self, logTemplate='', logIDL=[]):
        self.logTemplate = logTemplate
        self.logIDL = logIDL


# 字符级别规则
RULE_TABLE = {
    ' ': lambda t: ' ' in t,
    '_': lambda t: '_' in t,
    '*': lambda t: '*' in t,
    ':': lambda t: ':' in t,
    '/': lambda t: '/' in t,
    '(': lambda t: '(' in t,
    '{': lambda t: '{' in t,
    '[': lambda t: '[' in t,
    '.': lambda t: '.' in t,
    '=': lambda t: '=' in t,
    '-': lambda t: '-' in t,
    '+': lambda t: '+' in t,
    ',': lambda t: ',' in t,
    '\'': lambda t: '\'' in t,
    '"': lambda t: '"' in t,
    ';': lambda t: ';' in t,
    '?': lambda t: '?' in t,
    '!': lambda t: '!' in t,
    '$': lambda t: '$' in t,
    '<': lambda t: '<' in t,
    '>': lambda t: '>' in t,
    '@': lambda t: '@' in t,
    '|': lambda t: '|' in t,
    '#': lambda t: '#' in t,
    # 'ip': lambda t: re.match(r'(\d+\.){3}\d+(:\d+)?', t) is not None,
}
# 根据符号查询数组下标
RULE_IDX = {}
for idx, sym in enumerate(RULE_TABLE):
    RULE_IDX[sym] = idx
# 位图
# -1 -2 -3几个索引分别表示 token 数量为1 2 3
BITMAP = [0] * (len(RULE_TABLE) + 3)


def calc_signature(content: str) -> int:
    def _bitmap_to_number(_bitmap: List):
        _res = 0
        for _digit in _bitmap:
            _digit = 1 if _digit else 0
            _res = 2 * _res + _digit
        return _res

    this_bitmap = BITMAP.copy()
    this_token_list = content.split()
    # 处理token数量
    if len(this_token_list) <= 3:
        this_bitmap[-len(this_token_list)] = 1
    # 处理字符级别特征
    for token in this_token_list:
        for idx, rule in enumerate(RULE_IDX):
            if this_bitmap[idx] == 0:
                is_match = RULE_TABLE[rule](token)
                this_bitmap[idx] = int(is_match)
    return _bitmap_to_number(this_bitmap)


# 返回类型编号
def insert_into_bin(content: str, bin_list: List, logId) -> int:
    content_token_list = content.split()
    match_idx = -1
    match_lcs = []
    for idx, lcs_object in enumerate(bin_list):
        cur_lcs = LCS(content_token_list, lcs_object.logTemplate.split())
        if len(cur_lcs) > len(match_lcs):
            match_lcs = cur_lcs
            match_idx = idx
    # 未匹配
    if match_idx == -1 or len(match_lcs) < 2:
        bin_list.append(LCSObject(content, [logId]))
        return len(bin_list)
    else:
        bin_list[match_idx].logTemplate = ' '.join(match_lcs)
        bin_list[match_idx].logIDL.append(logId)
        return match_idx


# 读入数据
this_dataset = config.DATASET.Hadoop.value
CSV_FILE_PATH = '../../logs/%s/%s_2k.log_structured.csv' % (this_dataset, this_dataset)
df = pd.read_csv(CSV_FILE_PATH)
# 可能不存在
df.drop(['Date', 'Time', 'Pid', 'Level', 'Component', 'EventId'], axis=1, inplace=True, errors='ignore')
# df.drop_duplicates(subset=['EventId'], keep='first', inplace=True)

result = defaultdict(list)
bin_list = defaultdict(list)
parsed_event_id = pd.Series([0] * len(df))
# 开始解析每一行
for idx, row in enumerate(df.itertuples()):
    this_signature = calc_signature(row.Content)
    # result[this_signature].append(row.EventId)
    bin_idx = insert_into_bin(row.Content, bin_list[this_signature], row.LineId)
    parsed_event_id[idx] = this_signature * 100 + bin_idx

# result_details = [df[df['EventId'].isin(result[sig])]['Content'].tolist() for sig in result]
# result_more_than_ten = [template_list for template_list in result_details if len(template_list) > 10]

df['EventId'] = parsed_event_id

# df.sort_values('EventId').to_csv('./test.csv')
df.to_csv('./test.csv')

F1_measure, accuracy = evaluator.evaluate(CSV_FILE_PATH, './test.csv')
print(F1_measure, accuracy)

# print(len(result_details))
# print(result_more_than_ten)
