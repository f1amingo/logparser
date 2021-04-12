from typing import List

# 字符级别规则
RULE_TABLE = {
    ' ': lambda t: ' ' in t,
    '.': lambda t: '.' in t,
    '-': lambda t: '-' in t,
    '_': lambda t: '_' in t,
    '*': lambda t: '*' in t,
    ':': lambda t: ':' in t,
    '/': lambda t: '/' in t,
    '(': lambda t: '(' in t,
    '{': lambda t: '{' in t,
    '[': lambda t: '[' in t,
    '=': lambda t: '=' in t,
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
