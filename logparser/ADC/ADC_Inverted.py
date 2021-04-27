import collections
import os
import re
import pandas as pd
from datetime import datetime
from .log_signature import calc_signature


class LogCluster:
    def __init__(self):
        self.template_list = []
        self.inverted_dict = collections.defaultdict(list)


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
    def __init__(self, log_format, indir='./', outdir='./result/', rex=None, keep_para=True):
        """
        Attributes
        ----------
            rex : regular expressions used in preprocessing (step1)
            path : the input path stores the input log file name
            log_name : the name of the input file containing raw log messages
            save_path : the output path stores the file containing structured logs
        """
        self.path = indir
        self.log_name = None
        self.save_path = outdir
        self.df_log = None
        self.log_format = log_format
        self.rex = [] if rex is None else rex
        self.keep_para = keep_para

    def outputEventId(self, event_id_list):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.df_log['EventId'] = event_id_list
        self.df_log.to_csv(os.path.join(self.save_path, self.log_name + '_structured.csv'), index=False)

    # 根据倒排索引找到模板簇内索引
    def find_template(self, log_cluster: LogCluster, content: str) -> int:
        score_list = [0] * len(log_cluster.template_list)
        max_idx = None
        max_score = 0
        split_list = content.split()
        for token in split_list:
            if token in log_cluster.inverted_dict:
                for i in log_cluster.inverted_dict[token]:
                    score_list[i] += 1
                    if score_list[i] > max_score:
                        max_score = score_list[i]
                        max_idx = i
        if len(split_list) <= 2 and max_score >= 1:
            return max_idx
        if len(split_list) > 2 and max_score >= 2:
            return max_idx
        return None

    # 把模板添加到簇内
    def add_template(self, log_cluster: LogCluster, content: str) -> int:
        template_idx = len(log_cluster.template_list)
        log_cluster.template_list.append(content)
        split_list = content.split()
        for token in split_list:
            log_cluster.inverted_dict[token].append(template_idx)
        return template_idx

    def parse(self, log_name: str):
        print('Parsing file: ' + os.path.join(self.path, log_name))
        start_time = datetime.now()
        self.log_name = log_name
        signature_dict = collections.defaultdict(LogCluster)
        # 解析结果，列表保存
        eventId_list = []
        self.load_data()

        # 遍历每一行
        for idx, line in self.df_log.iterrows():
            log_content = line['Content']
            log_sig = calc_signature(log_content)
            log_cluster = signature_dict[log_sig]
            template_idx = self.find_template(log_cluster, log_content)
            if template_idx is None:
                template_idx = self.add_template(log_cluster, log_content)
            else:
                pass
            eventId_list.append(log_sig * 100 + template_idx)

            count = idx + 1
            if count % 1000 == 0 or count == len(self.df_log):
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))

        self.outputEventId(eventId_list)
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
