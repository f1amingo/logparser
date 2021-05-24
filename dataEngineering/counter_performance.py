# Method1: using count
import timeit
from collections import Counter

CHAR_DICT = {
    ' ': 0,
    '=': 0,
    ',': 0,
    ':': 0,
    ';': 0,
    '"': 0,
    '*': 0,
    '|': 0,
    '(': 0,
    '[': 0,
}


def method1(seq):
    base = 0
    for ch in CHAR_DICT:
        base = base * 100 + seq.count(ch)
    return base


# method 2: using a loop
def method2(seq):
    char_dict = CHAR_DICT.copy()  # char-level feature
    base = 0
    for ch in seq:
        if ch in char_dict:
            char_dict[ch] += 1
    for k, v in char_dict.items():
        base = 100 * base + v

    return base


if __name__ == '__main__':
    long_seq = ' =,:;""*|()[]1234567890qwertyuiop'
    assert method1(long_seq) == method2(long_seq)

    print(timeit.timeit("method1(long_seq)", setup='from __main__ import method1, long_seq', number=100000))
    print(timeit.timeit("method2(long_seq)", setup='from __main__ import method2, long_seq', number=100000))
