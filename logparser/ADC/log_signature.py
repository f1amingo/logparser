import collections

# 只要不会在变量中出现就可以
# '.' '-' 不可以
# '(' '#' Thunderbird
# '/' Mac 200行
# ':' Android E41
# '*' Mac E53

CHAR_LIST = [
    '=',
    ';',
    '"',
    '*',
]

TOKEN_LIST = [
    'true',  # Android
    'SPP.',  # Windows E35
    '\'Active\'',  # Mac E258
]

CHAR_DICT = {k: 0 for k in CHAR_LIST}
TOKEN_DICT = {k: 0 for k in TOKEN_LIST}


def dict2Int(dic: dict, base: int = 0) -> int:
    for v in dic.values():
        digit = 0 if v == 0 else 1
        base = 2 * base + digit
    return base


def calc_signature(token_list: list) -> int:
    char_dict = CHAR_DICT.copy()  # 字符级别
    token_dict = TOKEN_DICT.copy()  # token级别

    for token in token_list:
        for ch in token:
            if ch in char_dict:
                char_dict[ch] += 1
        if token in TOKEN_DICT:
            token_dict[token] += 1

    base = dict2Int(char_dict, 0)
    base = dict2Int(token_dict, base)
    # 长度信息
    base = base * 100 + len(token_list)
    return base


def char_counter(s: str) -> dict:
    res_dict = collections.defaultdict(int)
    for c in s:
        if c in CHAR_DICT:
            res_dict[c] += 1
    return res_dict


if __name__ == '__main__':
    pass
