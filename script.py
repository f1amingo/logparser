import re

# s1 = "Skipping, withExcluded: false, tr.intent:Intent { act=<*> flg=<*> cmp=<*> (has extras) }"
# s2 = "Skipping, withExcluded: false, tr.intent:Intent { flg=<*> cmp=<*> bnds=<*> }"
# res = filter(None, re.split('(\W)', s))
# res1 = re.split('([ =,:])', s1)
# res2 = re.split('([ =,:])', s2)
# print(res1)
# print(res2)

# for seq in ['tag="View Lock"', 'tag="RILJ_ACK_WL"', 'tag="*launch*"', 'tag="WiredAccessoryManager"']:
#     assert re.sub(r'"(.*)"', '<*>', 'tag="View Lock"') == 'tag=<*>'

s1 = 'a  =1'
res = re.split(r'([\s+|=])', s1)
print(res)
