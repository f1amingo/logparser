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

foo = "com.apple.icloud.fmfd.heartbeat: scheduler_evaluate_activity told me to run this job; however, but the start time isn't for 424575 seconds.  Ignoring."
s = "com.apple.ical.sync.x-coredata://DB05755C-483D-44B7-B93B-ED06E57FF420/CalDAVPrincipal/p11: scheduler_evaluate_activity told me to run this job; however, but the start time isn't for 59 seconds.  Ignoring."
res = re.sub(r'^com.apple.*:', '<*>', s)
print(res)
print(re.sub(r'^com.apple(.*:)+', '<*>', foo))
