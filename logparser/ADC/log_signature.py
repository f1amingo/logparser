import collections
import re

# 只要不会在变量中出现就可以
# '.' '-' 不可以
CHAR_LIST = [
    # '=',
    # '/',
    # '<',
    # '+', '*', '>',
    # ',', ';', ':', '\'', '"',
    # '#', Thunderbird
    # '?', '!', '$', '@', '|',
    # '(', Thunderbird Proxifier
    # '{', '[',
]
TOKEN_LIST = [
    # 'user=guest'  # Linux E18
    # , 'user=root'  # E19
    # , 'user=test'  # E20
    # , '(reserved)'  # E20
    # , 'hub'  # E110
    # , '(run-parts'  # Thunderbird
    # , "'Active'"  # Mac E258
    # , "Authenticated"  # Mac E163
    # , "Evaluating"  # Mac E164
    # , "HealthApp"  # Mac E7
]
SPECIAL_LIST = [
    # '^[A-Z]+$',
    # '\d+',
    # '\d+(\.\d+)?',
    # '.*\.$',  # 以点结尾

    # '^LOGIN*'  # linux E104
    # , '^RoamFail*'  # Mac E168
    # , '^AssocFail*'  # Mac E169
    # , '^DeauthInd*'  # Mac E170
]

CHAR_DICT = {k: 0 for k in CHAR_LIST}
TOKEN_DICT = {k: 0 for k in TOKEN_LIST}
SPECIAL_DICT = {k: 0 for k in SPECIAL_LIST}


def calc_signature(content: str) -> int:
    def dict2Int(dic: dict, base: int = 0) -> int:
        for v in dic.values():
            digit = 0 if v == 0 else 1
            base = 2 * base + digit
        return base

    # 字符级别
    char_dict = CHAR_DICT.copy()
    for ch in content:
        if ch in char_dict:
            char_dict[ch] += 1
    # token级别
    token_dict = TOKEN_DICT.copy()
    split_list = content.split()
    special_dict = SPECIAL_DICT.copy()
    for token in split_list:
        if token in TOKEN_DICT:
            token_dict[token] += 1
        # 正则表达式特殊规则
        for regex in SPECIAL_LIST:
            if re.match(regex, token):
                special_dict[regex] += 1

    base = dict2Int(char_dict, 0)
    base = dict2Int(token_dict, base)
    base = dict2Int(special_dict, base)

    # 长度信息
    base *= 10
    # 长度小于5，否则可能是变长变量
    if len(split_list) < 6:
        base += len(split_list)
    return base


def char_counter(s: str) -> dict:
    res_dict = collections.defaultdict(int)
    for c in s:
        if c in CHAR_DICT:
            res_dict[c] += 1
    return res_dict


if __name__ == '__main__':
    str1 = "com.apple.icloud.fmfd.heartbeat: scheduler_evaluate_activity told me to run this job; however, but the start time isn't for 439034 seconds.  Ignoring."
    str2 = "com.apple.ical.sync.x-coredata://DB05755C-483D-44B7-B93B-ED06E57FF420/CalDAVPrincipal/p11: scheduler_evaluate_activity told me to run this job; however, but the start time isn't for 59 seconds.  Ignoring."
    dict1 = char_counter(str1)
    dict2 = char_counter(str2)
    print(calc_signature(str1))
    print(calc_signature(str2))
