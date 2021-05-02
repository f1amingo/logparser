import collections
import hashlib
import os
import re
import pandas as pd
from datetime import datetime
from typing import List
from .log_signature import calc_signature


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
        """
        Attributes
        ----------
            rex : regular expressions used in preprocessing (step1)
            path : the input path stores the input log file name
            depth : depth of all leaf nodes
            st : similarity threshold
            maxChild : max number of children of an internal node
            log_name : the name of the input file containing raw log messages
            save_path : the output path stores the file containing structured logs
        """
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

    # seq1 is template
    def seqDist(self, seq1, seq2):
        if len(seq1) != len(seq2):
            print(seq1)
            print(seq2)
        assert len(seq1) == len(seq2)
        simTokens = 0
        numOfPar = 0

        for token1, token2 in zip(seq1, seq2):
            if token1 == '<*>':
                numOfPar += 1
                continue
            if token1 == token2:
                simTokens += 1

        # 用 NMD float
        # retVal = float(simTokens) / len(seq1)
        retVal = int(simTokens) / len(seq1)

        return retVal, numOfPar

    def fastMatch(self, template_list, seq):
        maxSim = -1
        maxNumOfPara = -1
        max_template = None
        maxIdx = -1  # 匹配的簇对应的索引

        for i, template in enumerate(template_list):
            # 相似度，变量数目
            curSim, curNumOfPara = self.seqDist(template, seq)
            # 选择相似度最大的，
            # 如果相同选择变量数目更多的？
            if curSim > maxSim or (curSim == maxSim and curNumOfPara > maxNumOfPara):
                maxSim = curSim
                maxNumOfPara = curNumOfPara
                max_template = template
                maxIdx = i

        if maxSim < self.st:
            return -1, None
        else:
            return maxIdx, max_template

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
            # log_token_list = self.preprocess(log_content).strip().split()
            log_token_list = log_content.split()
            log_sig = calc_signature(log_content)
            template_list = bin_dict[log_sig]
            template_idx, template = self.fastMatch(template_list, log_token_list)
            if template_idx == -1:
                template_idx = len(template_list)
                template_list.append(log_token_list)
            else:
                # 更新
                new_template_token_list = get_template(log_token_list, template)
                template_list[template_idx] = new_template_token_list

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
