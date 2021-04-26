import re

import seaborn as sns
import matplotlib.pyplot as plt

split_list = re.split('[ =|]', 'a b=c|d')
print(split_list)
