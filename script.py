import re

import seaborn as sns
import matplotlib.pyplot as plt

# split_list = re.split('[ =|]', 'a b=c|d')
# print(split_list)

for seq in ['tag="View Lock"', 'tag="RILJ_ACK_WL"', 'tag="*launch*"', 'tag="WiredAccessoryManager"']:
    assert re.sub(r'"(.*)"', '<*>', 'tag="View Lock"') == 'tag=<*>'

res = re.sub(r'[0-9]+', '<*>', 'tag =38')
print(res)
