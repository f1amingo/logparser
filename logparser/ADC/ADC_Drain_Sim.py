import collections
import os
import re
import pandas as pd
from datetime import datetime
from typing import List
from .log_signature import calc_signature, calc_signature_list


def log_sim(token_list1: list, token_list2: list) -> (float, float):
    m, n = len(token_list1), len(token_list2)
    if m != n:
        return 0, 0
    # 利用首token信息
    if token_list1[0] != token_list2[0]:
        return 0, 0
    count = 0
    for i in range(n):
        if token_list1[i] == token_list2[i]:
            count += 1
    return count / m, 0


# 一个叶子节点就是一个LogCluster
class LogCluster:
    def __init__(self, template_token_list: List[str], log_id_list: List[int]):
        self.template_token_list = template_token_list
        self.log_id_list = log_id_list
        self.template_id = None


def get_template(seq1, seq2):
    assert len(seq1) == len(seq2)
    res = []
    for t1, t2 in zip(seq1, seq2):
        if t1 == t2:
            res.append(t1)
        else:
            res.append('<*>')
    return res


class LogParser:
    def __init__(self, log_format, indir='./', outdir='./result/', depth=4, st=0.4,
                 maxChild=100, rex=None, keep_para=True):
        self.path = indir
        self.depth = depth - 2
        self.st = st
        self.maxChild = maxChild
        self.log_name = None
        self.save_path = outdir
        self.df_log = None
        self.log_format = log_format
        self.rex = [] if rex is None else rex
        self.keep_para = keep_para

    def fastMatch(self, template_list, seq):
        max_idx = -1
        max_foo, max_bar = 0, 0

        for i, template in enumerate(template_list):
            forward, backward = log_sim(template, seq)
            if forward + backward > max_foo + max_bar:
                max_idx = i
                max_foo, max_bar = forward, backward

        if max_foo > self.st:
            return max_idx, template_list[max_idx]
        return -1, None

    def outputEventId(self, event_id_list):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.df_log['EventId'] = event_id_list
        self.df_log.to_csv(os.path.join(self.save_path, self.log_name + '_structured.csv'), index=False)

    def parse(self, log_name: str):
        print('Parsing file: ' + os.path.join(self.path, log_name))
        start_time = datetime.now()
        self.log_name = log_name
        bin_dict = collections.defaultdict(list)
        # 保存解析的EventId
        event_id_list = []
        self.load_data()

        # 遍历每一行
        for idx, line in self.df_log.iterrows():
            log_content = line['Content']
            log_id = line['LineId']
            log_content = self.preprocess(log_content).strip()
            # log_token_list = list(filter(lambda x: x != '' and x != ' ', re.split('([ =,:])', log_content)))
            log_token_list = re.split('([( +)=,:])', log_content)
            log_sig = calc_signature_list(log_token_list)
            template_list = bin_dict[log_sig]
            template_idx, template_token_list = self.fastMatch(template_list, log_token_list)
            if template_idx == -1:
                # 没有匹配上
                template_idx = len(template_list)
                template_list.append(log_token_list)
            else:
                # 更新
                # new_template_token_list = get_template(log_token_list, template)
                # template_list[template_idx] = new_template_token_list
                pass

            event_id_list.append(log_sig * 1000 + template_idx)

            count = idx + 1
            if count % 1000 == 0 or count == len(self.df_log):
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))

        self.outputEventId(event_id_list)
        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - start_time))

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.log_format)
        self.df_log = self.log_to_dataframe(os.path.join(self.path, self.log_name), regex, headers, self.log_format)

    def preprocess(self, line):
        for currentRex in self.rex:
            line = re.sub(currentRex, '<*>', line)
        # 替换连续空格
        line = re.sub('\s+', ' ', line)
        return line

    def log_to_dataframe(self, log_file, regex, headers, logformat):
        """ Function to transform log file to dataframe 
        """
        log_messages = []
        linecount = 0
        with open(log_file, 'r') as fin:
            for line in fin.readlines():
                try:
                    match = regex.search(line.strip())
                    message = [match.group(header) for header in headers]
                    log_messages.append(message)
                    linecount += 1
                except Exception as e:
                    pass
        logdf = pd.DataFrame(log_messages, columns=headers)
        logdf.insert(0, 'LineId', None)
        logdf['LineId'] = [i + 1 for i in range(linecount)]
        return logdf

    def generate_logformat_regex(self, logformat):
        """ Function to generate regular expression to split log messages
        """
        headers = []
        splitters = re.split(r'(<[^<>]+>)', logformat)
        regex = ''
        for k in range(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(' +', '\\\s+', splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip('<').strip('>')
                regex += '(?P<%s>.*?)' % header
                headers.append(header)
        regex = re.compile('^' + regex + '$')
        return headers, regex

    def get_parameter_list(self, row):
        template_regex = re.sub(r"<.{1,5}>", "<*>", row["EventTemplate"])
        if "<*>" not in template_regex: return []
        template_regex = re.sub(r'([^A-Za-z0-9])', r'\\\1', template_regex)
        template_regex = re.sub(r'\\ +', r'\s+', template_regex)
        template_regex = "^" + template_regex.replace("\<\*\>", "(.*?)") + "$"
        parameter_list = re.findall(template_regex, row["Content"])
        parameter_list = parameter_list[0] if parameter_list else ()
        parameter_list = list(parameter_list) if isinstance(parameter_list, tuple) else [parameter_list]
        return parameter_list
