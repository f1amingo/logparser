from logparser.ADC.ADC_Fast import log_split, log_similarity

# '<$>()<-1> : getImeiV2 memory:868404020067521'
tem = ['<$>', '(', '', ')', '<-1>', ' ', '', ':', '', ' ', '<$>', '<$>', '<$>', '<$>', '<$>']
log = ['<$>', '(', '', ')', '<-1>', ' ', '', ':', '', ' ', 'getImeiV2', ' ', 'memory', ':', '868404020067521']
a = log_similarity(tem, log, 5)
print(a)
