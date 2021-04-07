<<<<<<< HEAD
RULE_TABLE = {
    'PacketResponder': lambda t: 'PacketResponder' == t,
}
s = 'PacketResponder <*> for block blk_<*> terminating'
s_list = s.split()
for t in s_list:
    for rule in RULE_TABLE:
        print(int(RULE_TABLE[rule](t)))
=======
RULE_TABLE = {
    'PacketResponder': lambda t: 'PacketResponder' == t,
}
s = 'PacketResponder <*> for block blk_<*> terminating'
s_list = s.split()
for t in s_list:
    for rule in RULE_TABLE:
        print(int(RULE_TABLE[rule](t)))
>>>>>>> ef98b6dc1ee508ff3a82c9b14e7856626069661c
