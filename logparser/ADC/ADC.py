import collections
import re
from typing import List
from logparser.utils.dataset import *
from .log_signature import calc_signature_list


class LogCluster:
    # LogCluster keeps a list of template with the same signature
    def __init__(self):
        self.template_list = []


class LogParser:
    def __init__(self, **kwargs):
        self.dataset = kwargs['dataset']
        self.log_format = LOG_FORMAT[self.dataset]
        self.in_path = log_path_raw(self.dataset)
        if 'out_path' in kwargs:
            self.out_path = kwargs['out_path']
        else:
            # default out path
            self.out_path = os.path.join('ADC_result', self.dataset.value + '_structured.csv')

        self.rex = kwargs['rex']
        self.st = kwargs['st']
        self.pre = kwargs['pre']
        self.keep_para = kwargs.get('keep_para', False)

        self.log_name = None
        self.df_log = None
        self.log_cluster_dict = None

    def parse(self):
        self.load_data()
        self.log_cluster_dict = collections.defaultdict(LogCluster)
        eventId_list = []

        for idx, line in self.df_log.iterrows():
            log_content = self.preprocess(line['Content'])
            log_token_list = self.split(log_content)
            log_sig = self.calc_signature(log_token_list)
            log_cluster = self.log_cluster_dict[log_sig]
            template_idx, template_token_list = self.search(log_cluster, log_token_list)
            if template_idx == -1:
                template_idx = self.add_template(log_cluster, log_token_list)
            else:
                updated_template = self.new_template_from(log_token_list, template_token_list)
                self.update_template(log_cluster, updated_template, template_idx)
            this_eventId = log_sig * 1000 + template_idx
            eventId_list.append(this_eventId)

        self.dump_result(eventId_list)
        return self.out_path

    def preprocess(self, log_content: str) -> str:
        for currentRex in self.rex:
            log_content = re.sub(currentRex, '<*>', log_content)
        # 替换连续空格
        line = re.sub('\s+', ' ', log_content)
        return line

    def split(self, log_content: str) -> List[str]:
        return re.split('([ =,:()\[\]])', log_content)

    def calc_signature(self, token_list: List[str]) -> int:
        return calc_signature_list(token_list)

    def search(self, log_cluster: LogCluster, token_list: List[str]) -> (int, List[str]):
        def log_sim(token_list1: list, token_list2: list) -> (float, float):
            m, n = len(token_list1), len(token_list2)
            if m != n:
                return 0, 0
            # 利用前缀信息
            for i in range(min(self.pre, n)):
                if token_list1[i] != token_list2[i]:
                    return 0, 0
            count = self.pre
            for i in range(self.pre, n):
                if token_list1[i] == '<*>' or token_list1[i] == token_list2[i]:
                    count += 1
            return count / m, 0

        max_score = 0
        max_idx = -1
        for i, template in enumerate(log_cluster.template_list):
            score, _ = log_sim(template, token_list)
            if score > max_score:
                max_idx = i
                max_score = score

        if max_score > self.st:
            return max_idx, log_cluster.template_list[max_idx]
        return -1, None

    def add_template(self, log_cluster: LogCluster, token_list: List[str]) -> int:
        log_cluster.template_list.append(token_list)
        return len(log_cluster.template_list) - 1

    def new_template_from(self, log_token_list: List[str], template_token_list: List[str]) -> List[str]:
        assert len(log_token_list) == len(template_token_list)
        new_token_list = []
        for t1, t2 in zip(log_token_list, template_token_list):
            if t1 == t2:
                new_token_list.append(t1)
            else:
                new_token_list.append('<*>')
        return new_token_list

    def update_template(self, log_cluster: LogCluster, token_list: List[str], idx: int):
        log_cluster.template_list[idx] = token_list

    def dump_result(self, eventId_list):
        out_dir = os.path.dirname(self.out_path)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.df_log['EventId'] = eventId_list
        self.df_log.to_csv(self.out_path, index=False)

    def load_data(self):
        def generate_log_format_regex(log_format):
            """ Function to generate regular expression to split log messages
            """
            headers = []
            splitters = re.split(r'(<[^<>]+>)', log_format)
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

        def log_to_dataframe(log_file, regex, headers):
            """ Function to transform log file to dataframe
            """
            log_messages = []
            line_count = 0
            with open(log_file, 'r') as fin:
                for line in fin.readlines():
                    try:
                        match = regex.search(line.strip())
                        message = [match.group(header) for header in headers]
                        log_messages.append(message)
                        line_count += 1
                    except Exception as e:
                        pass
            log_df = pd.DataFrame(log_messages, columns=headers)
            log_df.insert(0, 'LineId', None)
            log_df['LineId'] = [i + 1 for i in range(line_count)]
            return log_df

        headers, regex = generate_log_format_regex(self.log_format)
        self.df_log = log_to_dataframe(self.in_path, regex, headers)
