import collections
import re
from datetime import datetime
from typing import List
from logparser.utils.dataset import *

DELIMITER = re.compile('([\s=,:;|()\[\]])')
VAR = '<$>'  # replace variable with

CHAR_DICT = [
    '|',
    '"',
    '(',
    '*',
    ';',
    ',',
    '=',
    ':',
    ' ',
]


def hasNumbers(s):
    return any(ch.isdigit() for ch in s)


def log_signature(content: str, log_token_list) -> int:
    base = 0
    for ch in CHAR_DICT:
        base = base * 100 + content.count(ch)
    # word_list1 = [w for w in log_token_list if w not in CHAR_DICT]
    # len_list = [len(token) for token in word_list1 if not hasNumbers(token)]
    # max_len = max(len_list) if len_list else 0
    # 首个token
    # base = base * 100 + len(log_token_list[0])

    # 找到第一个不含数字
    # head = 0
    # for token in log_token_list:
    #     if all(ch.isalpha() for ch in token):
    #         head = len(token)
    #         break
    # tail = 0
    # count = 2
    # for token in log_token_list[::-1]:
    #     if all(ch.isalpha() for ch in token):
    #         tail = len(token)
    #         count -= 1
    #         if count == 0:
    #             break
    # base = base * 100 + head
    # base = base * 100 + tail
    return base


def log_split(log_content: str):
    return DELIMITER.split(log_content)


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
            self.out_path = os.path.join('ADC_New_result', self.dataset.value + '_structured.csv')

        self.rex = [re.compile(r) for r in kwargs['rex']]
        self.st = kwargs['st']
        self.pre = kwargs['pre']
        self.keep_para = kwargs.get('keep_para', False)

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
            log_content = self.preprocess(log_content).strip()

            log_token_list = DELIMITER.split(log_content)

            log_sig = log_signature(log_content, log_token_list)

            log_cluster = self.log_cluster_dict[log_sig]
            template_idx, template_token_list = self.search(log_cluster, log_token_list)
            if template_idx == -1:
                template_idx = self.add_template(log_cluster, log_token_list)
            else:
                updated_template = self.new_template_from(log_token_list, template_token_list)
                self.update_template(log_cluster, updated_template, template_idx)

            this_eventId = log_sig * 1000 + template_idx
            eventId_list.append(this_eventId)

            count = idx + 1
            if count % 1000 == 0:
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))

        self.dump_result(eventId_list)
        time_elapsed = datetime.now() - start_time
        print('Parsing done. [Time taken: {!s}]'.format(time_elapsed))
        return time_elapsed, self.out_path

    def preprocess(self, log_content: str) -> str:
        for r in self.rex:
            log_content = r.sub('<$>', log_content)
        if self.dataset.value == 'Linux':
            log_content = re.sub('\s+', ' ', log_content)
        return log_content

    def search(self, log_cluster: LogCluster, token_list: List[str]) -> (int, List[str]):

        def log_similarity(template_token_list: list, log_token_list: list) -> float:
            m, n = len(template_token_list), len(log_token_list)
            if m != n:
                return 0
            word_list1 = [w for w in template_token_list if w not in CHAR_DICT]
            word_list2 = [w for w in log_token_list if w not in CHAR_DICT]
            if len(word_list1) != len(word_list2):
                return 0
            size = len(word_list1)
            for i in range(min(self.pre, size)):
                if not hasNumbers(word_list2[i]) and word_list1[i] != word_list2[i] and word_list1[i] != VAR:
                    return 0
            intersect = set(word_list1) & set(word_list2)
            return len(intersect) / len(word_list1)

        # def log_similarity(template_token_list: list, log_token_list: list) -> float:
        #     m, n = len(template_token_list), len(log_token_list)
        #     if m != n:
        #         return 0
        #     word_list1 = [w for w in template_token_list if w not in CHAR_DICT]
        #     word_list2 = [w for w in log_token_list if w not in CHAR_DICT]
        #     # mark_list1 = [w for w in template_token_list if w in CHAR_DICT]
        #     # mark_list2 = [w for w in log_token_list if w in CHAR_DICT]
        #     # if mark_list1 != mark_list2:
        #     #     return 0
        #     if len(word_list1) != len(word_list2):
        #         return 0
        #     size = len(word_list1)
        #     count = 0
        #     for i in range(min(self.pre, size)):
        #         if not hasNumbers(word_list2[i]) and word_list1[i] != word_list2[i] and word_list1[i] != VAR:
        #             return 0
        #     for i in range(size):
        #         if word_list1[i] in [word_list2[i], VAR]:
        #             count += 1
        #     return count / size

        max_score = 0
        max_idx = -1
        for i, template in enumerate(log_cluster.template_list):
            score = log_similarity(template, token_list)
            if score > max_score:
                max_idx = i
                max_score = score

        if max_score >= self.st:
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
