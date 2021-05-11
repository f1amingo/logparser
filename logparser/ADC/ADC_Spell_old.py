"""
Description : This file implements the Spell algorithm for log parsing
Author      : LogPAI team
License     : MIT
"""
import collections
import hashlib
import os
import re
import string
from datetime import datetime
import pandas as pd
from .log_signature import calc_signature


class LCSObject:
    """ Class object to store a log group with the same template
    """

    def __init__(self, logTemplate, logIDL):
        self.logTemplate = logTemplate
        self.logIDL = logIDL


class Node:
    """ A node in prefix tree data structure
    """

    def __init__(self, token='', templateNo=0):
        self.logClust = None
        self.token = token
        self.templateNo = templateNo
        self.childD = dict()


class LogParser:
    """ LogParser class

    Attributes
    ----------
        path : the path of the input file
        logName : the file name of the input file
        savePath : the path of the output file
        tau : how much percentage of tokens matched to merge a log message
    """

    def __init__(self, indir='./', outdir='./result/', log_format=None, tau=0.5, rex=[], keep_para=True):
        self.path = indir
        self.logName = None
        self.savePath = outdir
        self.tau = tau
        self.logformat = log_format
        self.df_log = None
        self.rex = rex
        self.keep_para = keep_para

    def LCS(self, seq1, seq2):
        lengths = [[0 for j in range(len(seq2) + 1)] for i in range(len(seq1) + 1)]
        # row 0 and column 0 are initialized to 0 already
        for i in range(len(seq1)):
            for j in range(len(seq2)):
                if seq1[i] == seq2[j]:
                    lengths[i + 1][j + 1] = lengths[i][j] + 1
                else:
                    lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

        # read the substring out from the matrix
        result = []
        lenOfSeq1, lenOfSeq2 = len(seq1), len(seq2)
        while lenOfSeq1 != 0 and lenOfSeq2 != 0:
            if lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1 - 1][lenOfSeq2]:
                lenOfSeq1 -= 1
            elif lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1][lenOfSeq2 - 1]:
                lenOfSeq2 -= 1
            else:
                assert seq1[lenOfSeq1 - 1] == seq2[lenOfSeq2 - 1]
                result.insert(0, seq1[lenOfSeq1 - 1])
                lenOfSeq1 -= 1
                lenOfSeq2 -= 1
        return result

    def SimpleLoopMatch(self, logClustL, seq):
        for logClust in logClustL:
            if float(len(logClust.logTemplate)) < 0.5 * len(seq):
                continue
            # Check the template is a subsequence of seq (we use set checking as a proxy here for speedup since
            # incorrect-ordering bad cases rarely occur in logs)
            token_set = set(seq)
            if all(token in token_set or token == '<*>' for token in logClust.logTemplate):
                return logClust
        return None

    def PrefixTreeMatch(self, parentn, seq, idx):
        retLogClust = None
        length = len(seq)
        for i in range(idx, length):
            if seq[i] in parentn.childD:
                childn = parentn.childD[seq[i]]
                if (childn.logClust is not None):
                    constLM = [w for w in childn.logClust.logTemplate if w != '<*>']
                    if float(len(constLM)) >= self.tau * length:
                        return childn.logClust
                else:
                    return self.PrefixTreeMatch(childn, seq, i + 1)

        return retLogClust

    def LCSMatch(self, logClustL, seq):
        maxLen = -1
        maxClust = None
        maxIdx = -1
        set_seq = set(seq)
        size_seq = len(seq)
        for i, logClust in enumerate(logClustL):
            set_template = set(logClust.logTemplate)
            # 两个set中相同token的数量超过一半
            if len(set_seq & set_template) < 0.5 * size_seq:
                continue
            lcs = self.LCS(seq, logClust.logTemplate)
            # 选lcs最长的，如果lcs相同就选模板长度最小的
            if len(lcs) > maxLen or (len(lcs) == maxLen and len(logClust.logTemplate) < len(maxClust.logTemplate)):
                maxLen = len(lcs)
                maxClust = logClust
                maxIdx = i

        # LCS should be large then tau * len(itself)
        if float(maxLen) < self.tau * size_seq:
            return len(logClustL), None
        else:
            return maxIdx, maxClust

    def getTemplate(self, lcs, seq):
        retVal = []
        if not lcs:
            return retVal

        lcs = lcs[::-1]
        i = 0
        for token in seq:
            i += 1
            if token == lcs[-1]:
                retVal.append(token)
                lcs.pop()
            else:
                retVal.append('<*>')
            if not lcs:
                break
        if i < len(seq):
            retVal.append('<*>')
        return retVal

    def addSeqToPrefixTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if w != '<*>']

        for i in range(len(seq)):
            tokenInSeq = seq[i]
            # Match
            if tokenInSeq in parentn.childD:
                parentn.childD[tokenInSeq].templateNo += 1
                # Do not Match
            else:
                parentn.childD[tokenInSeq] = Node(token=tokenInSeq, templateNo=1)
            parentn = parentn.childD[tokenInSeq]

        if parentn.logClust is None:
            parentn.logClust = newCluster

    def removeSeqFromPrefixTree(self, rootn, newCluster):
        parentn = rootn
        seq = newCluster.logTemplate
        seq = [w for w in seq if w != '<*>']

        for tokenInSeq in seq:
            if tokenInSeq in parentn.childD:
                matchedNode = parentn.childD[tokenInSeq]
                if matchedNode.templateNo == 1:
                    del parentn.childD[tokenInSeq]
                    break
                else:
                    matchedNode.templateNo -= 1
                    parentn = matchedNode

    # 输出自定义结果
    def outputEventId(self, event_id_list):
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)
        self.df_log['EventId'] = event_id_list
        self.df_log.to_csv(os.path.join(self.savePath, self.logname + '_structured.csv'), index=False)

    # logClustL: List[LCSObject]
    # 一个LCSObject就是一类模板
    def outputResult(self, logClustL):
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)

        templates = [0] * self.df_log.shape[0]
        ids = [0] * self.df_log.shape[0]
        df_event = []  # 解析的模板结果

        for logclust in logClustL:
            template_str = ' '.join(logclust.logTemplate)
            eid = hashlib.md5(template_str.encode('utf-8')).hexdigest()[0:8]
            for logid in logclust.logIDL:
                templates[logid - 1] = template_str
                ids[logid - 1] = eid
            df_event.append([eid, template_str, len(logclust.logIDL)])

        df_event = pd.DataFrame(df_event, columns=['EventId', 'EventTemplate', 'Occurrences'])

        self.df_log['EventId'] = ids
        self.df_log['EventTemplate'] = templates
        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(self.get_parameter_list, axis=1)
        self.df_log.to_csv(os.path.join(self.savePath, self.logname + '_structured.csv'), index=False)
        df_event.to_csv(os.path.join(self.savePath, self.logname + '_templates.csv'), index=False)

    def parse(self, logname):
        start_time = datetime.now()
        print('Parsing file: ' + os.path.join(self.path, logname))
        self.logname = logname
        self.load_data()
        # 每个bin保存一个logCluster列表
        sig_bin = collections.defaultdict(list)
        # 保存根节点
        root_bin = {}
        # 保存解析的EventId
        event_id_list = []
        event_id_occurrence = collections.defaultdict(int)
        event_templates = {}

        for idx, line in self.df_log.iterrows():
            log_content = line['Content']
            log_sig = calc_signature(log_content)  # 计算签名
            logCluL = sig_bin[log_sig]
            if log_sig not in root_bin:
                root_bin[log_sig] = Node()
            rootNode = root_bin[log_sig]

            logID = line['LineId']
            logmessageL = list(filter(lambda x: x != '', re.split(r'[\s=:,]', self.preprocess(line['Content']))))

            match_idx, matchCluster = self.LCSMatch(logCluL, logmessageL)
            parsed_event_id = log_sig * 100 + match_idx
            if matchCluster is None:
                newCluster = LCSObject(logTemplate=logmessageL, logIDL=[logID])
                logCluL.append(newCluster)
                # 保存模板
                event_templates[parsed_event_id] = logmessageL
            else:
                cur_lcs = self.LCS(logmessageL, matchCluster.logTemplate)
                matchCluster.logTemplate = self.getTemplate(cur_lcs, matchCluster.logTemplate)
                matchCluster.logIDL.append(logID)
                # 保存模板
                event_templates[parsed_event_id] = matchCluster.logTemplate

            event_id_list.append(parsed_event_id)
            event_id_occurrence[parsed_event_id] += 1

            count = idx + 1
            if count % 1000 == 0 or count == len(self.df_log):
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))

        self.outputEventId(event_id_list)
        print('Parsing done. [Time taken: {!s}]'.format(datetime.now() - start_time))

        print(len(event_id_occurrence))
        print(event_id_occurrence)
        print([' '.join(event_templates[k]) for k in event_templates])

    def load_data(self):
        headers, regex = self.generate_logformat_regex(self.logformat)
        self.df_log = self.log_to_dataframe(os.path.join(self.path, self.logname), regex, headers, self.logformat)

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
                line = re.sub(r'[^\x00-\x7F]+', '<NASCII>', line)
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
                splitter = re.sub(' +', '\s+', splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip('<').strip('>')
                regex += '(?P<%s>.*?)' % header
                headers.append(header)
        regex = re.compile('^' + regex + '$')
        return headers, regex

    def get_parameter_list(self, row):
        template_regex = re.sub(r"\s<.{1,5}>\s", "<*>", row["EventTemplate"])
        if "<*>" not in template_regex: return []
        template_regex = re.sub(r'([^A-Za-z0-9])', r'\\\1', template_regex)
        template_regex = re.sub(r'\\ +', r'[^A-Za-z0-9]+', template_regex)
        template_regex = "^" + template_regex.replace("\<\*\>", "(.*?)") + "$"
        parameter_list = re.findall(template_regex, row["Content"])
        parameter_list = parameter_list[0] if parameter_list else ()
        parameter_list = list(parameter_list) if isinstance(parameter_list, tuple) else [parameter_list]
        parameter_list = [para.strip(string.punctuation).strip(' ') for para in parameter_list]
        return parameter_list
