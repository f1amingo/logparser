import re

import seaborn as sns
import matplotlib.pyplot as plt

s = 'a  =e'
# res = filter(None, re.split('(\W)', s))
# res = re.split('([(\s+)])', s)
res = re.sub('\s+',' ', s)
print(res)

# for seq in ['tag="View Lock"', 'tag="RILJ_ACK_WL"', 'tag="*launch*"', 'tag="WiredAccessoryManager"']:
#     assert re.sub(r'"(.*)"', '<*>', 'tag="View Lock"') == 'tag=<*>'

# s1 = 'com.apple.icloud.fmfd.heartbeat: abc '
# s2 = 'com.apple.ical.sync.x-coredata://DB05755C-483D-44B7-B93B-ED06E57FF420/CalDAVPrincipal/p11: abc'
#
# res = re.sub(r'(\w+\.){4,}', '<*>', s2)
# print(res)
