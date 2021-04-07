<<<<<<< HEAD
import re
import os
import hashlib
import pandas as pd
from datetime import datetime
from collections import defaultdict


class Event:
    def __init__(self, logidx, Eventstr=""):
        self.id = hashlib.md5(Eventstr.encode('utf-8')).hexdigest()[0:8]
        self.logs = [logidx]
        self.Eventstr = Eventstr
        self.EventToken = Eventstr.split()
        self.merged = False

    def refresh_id(self):
        self.id = hashlib.md5(self.Eventstr.encode('utf-8')).hexdigest()[0:8]


class LogParser:

    def __init__(self, indir, outdir, log_format, minEventCount=2, merge_percent=1,
                 rex=None, keep_para=True):
        """
            indir: the input directory of log file
            outdir: the output directory of parsing results
            log_format: prior knowledge about the log format
            minEventCount: the minimum number of events in a bin
            merge_percent: the percentage of different tokens
            rex: regular expressions used in preprocessing (step1)
            keep_para:
        """
        self.path = indir
        self.savePath = outdir
        self.logformat = log_format
        self.minEventCount = minEventCount
        self.merge_percent = merge_percent
        if rex is None:
            rex = []
        self.rex = rex
        self.keep_para = keep_para

        self.df_log = None
        self.logname = None  # the log file name under $indir
        self.merged_events = []
        self.bins = defaultdict(dict)

    def parse(self, logname):
        """
            parse the $logname file under $indir
        """
        start_time = datetime.now()
        print('Parsing file: ' + os.path.join(self.path, logname))
        self.logname = logname
        self.load_data()
        self.tokenize()
        # self.dump_content()
        self.dump()
        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - start_time))

    def tokenize(self):
        # tokenization
        # self.df_log['tokens'] = self.df_log['Content'].map(str.split)
        pass

    def dump_content(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)
        # 丢弃这几列
        # for _header in ['Date', 'Time', 'Pid', 'Level', 'Component']:
        #     self.df_log.drop(_header, axis=1, inplace=True)
        self.df_log.to_csv(os.path.join(self.savePath, self.logname + '_content.csv'), index=False)

    def dump(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)

        templateL = [0] * self.df_log.shape[0]
        idL = [0] * self.df_log.shape[0]
        df_events = []

        for event in self.merged_events:
            for logidx in event.logs:
                templateL[logidx] = event.Eventstr
                idL[logidx] = event.id
            df_events.append([event.id, event.Eventstr, len(event.logs)])

        df_event = pd.DataFrame(df_events, columns=['EventId', 'EventTemplate', 'Occurrences'])

        self.df_log['EventId'] = idL
        self.df_log['EventTemplate'] = templateL
        # self.df_log.drop("Content_", axis=1, inplace=True)
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(self.get_parameter_list, axis=1)
        self.df_log.to_csv(os.path.join(self.savePath, self.logname + '_structured.csv'), index=False)

        occ_dict = dict(self.df_log['EventTemplate'].value_counts())
        df_event = pd.DataFrame()
        df_event['EventTemplate'] = self.df_log['EventTemplate'].unique()
        df_event['EventId'] = df_event['EventTemplate'].map(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()[0:8])
        df_event['Occurrences'] = df_event['EventTemplate'].map(occ_dict)
        df_event.to_csv(os.path.join(self.savePath, self.logname + '_templates.csv'), index=False,
                        columns=["EventId", "EventTemplate", "Occurrences"])

    def load_data(self):
        def generate_logformat_regex(logformat):
            headers = []
            splitters = re.split(r'(<[^<>]+>)', logformat)
            regex = ''
            for k in range(len(splitters)):
                if k % 2 == 0:
                    splitter = re.sub(' +', '\s+', splitters[k])
                    regex += splitter
                else:
                    header = splitters[k].strip('<').strip('>')
                    regex += '(?P<%s>.*?)' % header
                    headers.append(header)
            regex = re.compile('^' + regex + '$')
            return headers, regex

        def log_to_dataframe(log_file, regex, headers, logformat):
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

        def preprocess(log):
            for currentRex in self.rex:
                log = re.sub(currentRex, '<*>', log)
            return log

        headers, regex = generate_logformat_regex(self.logformat)
        self.df_log = log_to_dataframe(os.path.join(self.path, self.logname), regex, headers, self.logformat)
        # self.df_log['Content_'] = self.df_log['Content'].map(preprocess)
=======
import re
import os
import hashlib
import pandas as pd
from datetime import datetime
from collections import defaultdict


class Event:
    def __init__(self, logidx, Eventstr=""):
        self.id = hashlib.md5(Eventstr.encode('utf-8')).hexdigest()[0:8]
        self.logs = [logidx]
        self.Eventstr = Eventstr
        self.EventToken = Eventstr.split()
        self.merged = False

    def refresh_id(self):
        self.id = hashlib.md5(self.Eventstr.encode('utf-8')).hexdigest()[0:8]


class LogParser:

    def __init__(self, indir, outdir, log_format, minEventCount=2, merge_percent=1,
                 rex=None, keep_para=True):
        """
            indir: the input directory of log file
            outdir: the output directory of parsing results
            log_format: prior knowledge about the log format
            minEventCount: the minimum number of events in a bin
            merge_percent: the percentage of different tokens
            rex: regular expressions used in preprocessing (step1)
            keep_para:
        """
        self.path = indir
        self.savePath = outdir
        self.logformat = log_format
        self.minEventCount = minEventCount
        self.merge_percent = merge_percent
        if rex is None:
            rex = []
        self.rex = rex
        self.keep_para = keep_para

        self.df_log = None
        self.logname = None  # the log file name under $indir
        self.merged_events = []
        self.bins = defaultdict(dict)

    def parse(self, logname):
        """
            parse the $logname file under $indir
        """
        start_time = datetime.now()
        print('Parsing file: ' + os.path.join(self.path, logname))
        self.logname = logname
        self.load_data()
        self.tokenize()
        # self.dump_content()
        self.dump()
        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - start_time))

    def tokenize(self):
        # tokenization
        # self.df_log['tokens'] = self.df_log['Content'].map(str.split)
        pass

    def dump_content(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)
        # 丢弃这几列
        # for _header in ['Date', 'Time', 'Pid', 'Level', 'Component']:
        #     self.df_log.drop(_header, axis=1, inplace=True)
        self.df_log.to_csv(os.path.join(self.savePath, self.logname + '_content.csv'), index=False)

    def dump(self):
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)

        templateL = [0] * self.df_log.shape[0]
        idL = [0] * self.df_log.shape[0]
        df_events = []

        for event in self.merged_events:
            for logidx in event.logs:
                templateL[logidx] = event.Eventstr
                idL[logidx] = event.id
            df_events.append([event.id, event.Eventstr, len(event.logs)])

        df_event = pd.DataFrame(df_events, columns=['EventId', 'EventTemplate', 'Occurrences'])

        self.df_log['EventId'] = idL
        self.df_log['EventTemplate'] = templateL
        # self.df_log.drop("Content_", axis=1, inplace=True)
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(self.get_parameter_list, axis=1)
        self.df_log.to_csv(os.path.join(self.savePath, self.logname + '_structured.csv'), index=False)

        occ_dict = dict(self.df_log['EventTemplate'].value_counts())
        df_event = pd.DataFrame()
        df_event['EventTemplate'] = self.df_log['EventTemplate'].unique()
        df_event['EventId'] = df_event['EventTemplate'].map(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()[0:8])
        df_event['Occurrences'] = df_event['EventTemplate'].map(occ_dict)
        df_event.to_csv(os.path.join(self.savePath, self.logname + '_templates.csv'), index=False,
                        columns=["EventId", "EventTemplate", "Occurrences"])

    def load_data(self):
        def generate_logformat_regex(logformat):
            headers = []
            splitters = re.split(r'(<[^<>]+>)', logformat)
            regex = ''
            for k in range(len(splitters)):
                if k % 2 == 0:
                    splitter = re.sub(' +', '\s+', splitters[k])
                    regex += splitter
                else:
                    header = splitters[k].strip('<').strip('>')
                    regex += '(?P<%s>.*?)' % header
                    headers.append(header)
            regex = re.compile('^' + regex + '$')
            return headers, regex

        def log_to_dataframe(log_file, regex, headers, logformat):
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

        def preprocess(log):
            for currentRex in self.rex:
                log = re.sub(currentRex, '<*>', log)
            return log

        headers, regex = generate_logformat_regex(self.logformat)
        self.df_log = log_to_dataframe(os.path.join(self.path, self.logname), regex, headers, self.logformat)
        # self.df_log['Content_'] = self.df_log['Content'].map(preprocess)
>>>>>>> ef98b6dc1ee508ff3a82c9b14e7856626069661c
