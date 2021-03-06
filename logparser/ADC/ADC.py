import collections
import re
from datetime import datetime
from typing import List
from logparser.utils.dataset import *

DELIMITERS = {' ', '=', ',', ':', '|', '(', ')', '[', ']', '\'', }
SPLIT_DELIMITER = '([' + ''.join(['\\' + k for k in DELIMITERS]) + '])'
delimiter = re.compile(SPLIT_DELIMITER)
VAR = '<$>'  # replace variable with

CHAR_LIST = [
    '=',
    ';',
    '"',
    '*',
    ',',
    '|',
    '(',
    # ')',
    '[',
    # ']',
]

TOKEN_LIST = [
    # 'false',  # Android
    # 'true',  # Android
    # 'SPP.',  # Windows E35
    # 'Active',  # Mac E258
    # 'HTTPS',  # Proxifier E1
    # 'with',  # Proxifier E4
    # 'has',  # BGL
    # # 'guest',  # Linux E17 conflict with OpenSSH
]


def set_TOKEN_LIST(token_list: list):
    global TOKEN_LIST, TOKEN_DICT
    TOKEN_LIST = token_list
    TOKEN_DICT = {k: 0 for k in TOKEN_LIST}


CHAR_DICT = {k: 0 for k in CHAR_LIST}
TOKEN_DICT = {k: 0 for k in TOKEN_LIST}


def dict2Int(dic: dict, base: int = 0) -> int:
    for v in dic.values():
        digit = 0 if v == 0 else 1
        base = 2 * base + digit
    return base


def log_split(log_content: str) -> List[str]:
    # return re.split('([ =,:()\[\]])', log_content)
    # return re.split(SPLIT_DELIMITER, log_content)
    return delimiter.split(log_content)


# def log_signature(seq_list: List[str], seq: str) -> int:
#     base = 0
#     for ch in CHAR_LIST:
#         base = base * 100 + seq.count(ch)
#     # base = base * 100 + len(seq_list)  # length feature
#     base = base * 10 + len(seq_list[0])
#     return base


def log_signature(token_list: List[str]) -> int:
    base = 0
    char_dict = CHAR_DICT.copy()  # char-level feature

    for token in token_list:
        for ch in token:
            if ch in char_dict:
                char_dict[ch] += 1

    base = dict2Int(char_dict, base)
    base = base * 100 + len(token_list)  # length feature
    base = base * 10 + len(token_list[0])
    return base


class LogCluster:
    # LogCluster keeps a list of template with the same signature
    def __init__(self):
        self.template_list = []


class LogParser:
    def __init__(self, **kwargs):
        self.dataset = kwargs['dataset']
        self.log_format = LOG_FORMAT[self.dataset]
        if 'in_path' in kwargs:
            self.in_path = kwargs['in_path']
        else:
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
        print('Parsing file: ', self.in_path)
        start_time = datetime.now()

        self.load_data()
        self.log_cluster_dict = collections.defaultdict(LogCluster)
        eventId_list = []

        for idx, line in self.df_log.iterrows():
            log_content = line['Content']
            # inline
            for currentRex in self.rex:
                log_content = re.sub(currentRex, '<$>', log_content)
            if self.dataset.value == 'linux':
                log_content = re.sub('\s+', ' ', log_content)
            # log_content = self.preprocess(line['Content'])

            # log_token_list = log_split(log_content)
            log_token_list = delimiter.split(log_content)

            log_sig = log_signature(log_token_list)
            # log_sig = 100 + len(log_token_list)  # length feature
            # log_sig = log_sig * 10 + len(log_token_list[0])

            log_cluster = self.log_cluster_dict[log_sig]
            template_idx, template_token_list = self.search(log_cluster, log_token_list)
            if template_idx == -1:
                # template_idx = self.add_template(log_cluster, log_token_list)
                log_cluster.template_list.append(log_token_list)
                template_idx = len(log_cluster.template_list) - 1
            else:
                # updated_template = self.new_template_from(log_token_list, template_token_list)
                # self.update_template(log_cluster, updated_template, template_idx)
                new_token_list = []
                for t1, t2 in zip(log_token_list, template_token_list):
                    if t1 == t2:
                        new_token_list.append(t1)
                    else:
                        new_token_list.append(VAR)
                log_cluster.template_list[template_idx] = new_token_list

            this_eventId = log_sig * 1000 + template_idx
            eventId_list.append(str(this_eventId))

            count = idx + 1
            if count % 1000 == 0:
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))

        self.dump_result(eventId_list)

        time_elapsed = datetime.now() - start_time
        print('Parsing done. [Time taken: {!s}]'.format(time_elapsed))
        return time_elapsed, self.out_path

    def preprocess(self, log_content: str) -> str:
        for currentRex in self.rex:
            log_content = re.sub(currentRex, '<$>', log_content)
        # 替换连续空格
        line = re.sub('\s+', ' ', log_content)
        return line

    def log_sim(self, token_list1: list, token_list2: list) -> float:
        m, n = len(token_list1), len(token_list2)
        if m != n:
            return 0
        # 利用前缀信息
        for i in range(min(self.pre, n)):
            if token_list1[i] != token_list2[i]:
                return 0
        count = self.pre
        for i in range(self.pre, n):
            # if token_list1[i] == VAR or token_list2[i] == VAR or token_list1[i] == token_list2[i]:
            #     count += 1
            # 符号否决
            isDel1 = token_list1[i] in DELIMITERS
            isDel2 = token_list2[i] in DELIMITERS
            if not isDel1 and not isDel2:
                if token_list1[i] == VAR or token_list2[i] == VAR or token_list1[i] == token_list2[i]:
                    count += 1
            elif isDel1 or isDel2:
                if token_list1[i] == token_list2[i]:
                    count += 1
                else:
                    return 0
        return count / m

    def search(self, log_cluster: LogCluster, token_list: List[str]) -> (int, List[str]):
        max_score = 0
        max_idx = -1
        for i, template in enumerate(log_cluster.template_list):
            score = self.log_sim(template, token_list)
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
                new_token_list.append(VAR)
        return new_token_list

    def update_template(self, log_cluster: LogCluster, token_list: List[str], idx: int):
        log_cluster.template_list[idx] = token_list

    def dump_result(self, eventId_list):
        if not eventId_list:
            return
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
        print('Regex generated.')
        self.df_log = log_to_dataframe(self.in_path, regex, headers)
        print('Data loaded.')
