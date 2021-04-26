"""
Description : This file implements the Drain algorithm for log parsing
Author      : LogPAI team
License     : MIT
"""

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


# 树节点
class Node:
    def __init__(self, childD=None, depth=0, digitOrToken=None):
        self.childD = {} if childD is None else childD
        self.depth = depth
        self.digitOrToken = digitOrToken
        self.template_count = 0


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

    def tree_search(self, root, token_list):
        seq_len = len(token_list)
        # 长度层，判断长度
        if seq_len not in root.childD:
            return 0, None
        len_node = root.childD[seq_len]  # 长度层的节点
        depth = 1
        for token in token_list:
            if depth >= self.depth or depth > seq_len:
                break
            if token in len_node.childD:
                len_node = len_node.childD[token]
            elif '<*>' in len_node.childD:
                len_node = len_node.childD['<*>']
            else:
                return 0, None
            depth += 1
        return self.fastMatch(len_node.childD, token_list)

    def addSeqToPrefixTree(self, rn, logClust):
        def has_number(s):
            return any(char.isdigit() for char in s)

        logClust.template_id = rn.template_count  # 模板id等于序号
        rn.template_count += 1  # 这个根上的模板总数加一

        seqLen = len(logClust.template_token_list)
        if seqLen not in rn.childD:
            firtLayerNode = Node(depth=1, digitOrToken=seqLen)
            rn.childD[seqLen] = firtLayerNode
        else:
            firtLayerNode = rn.childD[seqLen]

        parentn = firtLayerNode

        currentDepth = 1
        # 只有一个token时，结果是不对的
        for token in logClust.template_token_list:

            # Add current log cluster to the leaf node
            if currentDepth >= self.depth or currentDepth > seqLen:
                # if len(parentn.childD) == 0:
                #     parentn.childD = [logClust]
                # else:
                #     parentn.childD.append(logClust)
                break

            # If token not matched in this layer of existing tree. 
            if token not in parentn.childD:
                if not has_number(token):
                    if '<*>' in parentn.childD:
                        if len(parentn.childD) < self.maxChild:
                            newNode = Node(depth=currentDepth + 1, digitOrToken=token)
                            parentn.childD[token] = newNode
                            parentn = newNode
                        else:
                            parentn = parentn.childD['<*>']
                    else:
                        if len(parentn.childD) + 1 < self.maxChild:
                            newNode = Node(depth=currentDepth + 1, digitOrToken=token)
                            parentn.childD[token] = newNode
                            parentn = newNode
                        elif len(parentn.childD) + 1 == self.maxChild:
                            newNode = Node(depth=currentDepth + 1, digitOrToken='<*>')
                            parentn.childD['<*>'] = newNode
                            parentn = newNode
                        else:
                            parentn = parentn.childD['<*>']

                else:
                    if '<*>' not in parentn.childD:
                        newNode = Node(depth=currentDepth + 1, digitOrToken='<*>')
                        parentn.childD['<*>'] = newNode
                        parentn = newNode
                    else:
                        parentn = parentn.childD['<*>']

            # If the token is matched
            else:
                parentn = parentn.childD[token]

            currentDepth += 1

        # 添加到 logClusterList
        if len(parentn.childD) == 0:
            parentn.childD = [logClust]
        else:
            parentn.childD.append(logClust)

    # seq1 is template
    def seqDist(self, seq1, seq2):
        assert len(seq1) == len(seq2)
        simTokens = 0
        numOfPar = 0

        for token1, token2 in zip(seq1, seq2):
            if token1 == '<*>':
                numOfPar += 1
                continue
            if token1 == token2:
                simTokens += 1

        retVal = float(simTokens) / len(seq1)

        return retVal, numOfPar

    def fastMatch(self, logClustL, seq):
        retLogClust = None

        maxSim = -1
        maxNumOfPara = -1
        maxClust = None
        maxIdx = -1  # 匹配的簇对应的索引

        for i, logClust in enumerate(logClustL):
            curSim, curNumOfPara = self.seqDist(logClust.template_token_list, seq)
            if curSim > maxSim or (curSim == maxSim and curNumOfPara > maxNumOfPara):
                maxSim = curSim
                maxNumOfPara = curNumOfPara
                maxClust = logClust
                maxIdx = i

        if maxSim < self.st:
            return len(logClustL), None
        else:
            return maxIdx, maxClust
        # if maxSim >= self.st:
        #     retLogClust = maxClust
        # return retLogClust

    # 输出自定义结果
    def outputEventId(self, event_id_list):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.df_log['EventId'] = event_id_list
        self.df_log.to_csv(os.path.join(self.save_path, self.log_name + '_structured.csv'), index=False)

    def outputResult(self, logClustL):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        log_templates = [0] * self.df_log.shape[0]
        log_templateids = [0] * self.df_log.shape[0]
        df_events = []
        for logClust in logClustL:
            template_str = ' '.join(logClust.template_token_list)
            occurrence = len(logClust.log_id_list)
            # template_id = hashlib.md5(template_str.encode('utf-8')).hexdigest()[0:8]
            template_id = logClust.template_id
            for log_id in logClust.log_id_list:
                log_id -= 1
                log_templates[log_id] = template_str
                log_templateids[log_id] = template_id
            df_events.append([template_id, template_str, occurrence])

        # df_event = pd.DataFrame(df_events, columns=['EventId', 'EventTemplate', 'Occurrences'])
        self.df_log['EventId'] = log_templateids
        self.df_log['EventTemplate'] = log_templates

        if self.keep_para:
            self.df_log["ParameterList"] = self.df_log.apply(self.get_parameter_list, axis=1)
        self.df_log.to_csv(os.path.join(self.save_path, self.log_name + '_structured.csv'), index=False)

        occ_dict = dict(self.df_log['EventTemplate'].value_counts())
        df_event = pd.DataFrame()
        df_event['EventTemplate'] = self.df_log['EventTemplate'].unique()
        df_event['EventId'] = df_event['EventTemplate'].map(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()[0:8])
        # df_event['EventId'] = self.df_log['EventId'].unique()
        df_event['Occurrences'] = df_event['EventTemplate'].map(occ_dict)
        df_event.to_csv(os.path.join(self.save_path, self.log_name + '_templates.csv'), index=False,
                        columns=["EventId", "EventTemplate", "Occurrences"])

    def printTree(self, node, dep):
        pStr = ''
        for i in range(dep):
            pStr += '\t'

        if node.depth == 0:
            pStr += 'Root'
        elif node.depth == 1:
            pStr += '<' + str(node.digitOrToken) + '>'
        else:
            pStr += node.digitOrToken

        print(pStr)

        if node.depth == self.depth:
            return 1
        for child in node.childD:
            self.printTree(node.childD[child], dep + 1)

    def parse(self, log_name: str):
        print('Parsing file: ' + os.path.join(self.path, log_name))
        start_time = datetime.now()
        self.log_name = log_name
        # root_node = Node()
        all_cluster_list = []  # 所有的logCluster
        sig_bin = {}
        # 保存解析的EventId
        event_id_list = []

        self.load_data()

        # 遍历每一行
        for idx, line in self.df_log.iterrows():
            log_content = line['Content']
            log_id = line['LineId']
            if log_id == 298:
                a = 1
            # 预处理，token化
            log_token_list = self.preprocess(log_content).strip().split()
            # 计算签名
            log_sig = calc_signature(log_content)
            # log_sig = 0
            if log_sig not in sig_bin:
                sig_bin[log_sig] = Node()
            # 每个签名对应一颗树
            this_root = sig_bin[log_sig]

            # 搜索树，找到匹配的Cluster
            # matched_cluster = self.tree_search(root_node, log_token_list)
            match_idx, matched_cluster = self.tree_search(this_root, log_token_list)
            # parsed_event_id = log_sig * 100 + matched_cluster.template_id
            # event_id_list.append(parsed_event_id)
            # cluster_template_id = matched_cluster.template_id
            if matched_cluster is None:
                # 没有匹配的 Cluster
                new_cluster = LogCluster(template_token_list=log_token_list, log_id_list=[log_id])
                all_cluster_list.append(new_cluster)
                # self.addSeqToPrefixTree(root_node, new_cluster)
                self.addSeqToPrefixTree(this_root, new_cluster)

                cluster_template_id = new_cluster.template_id
            else:
                # 把日志消息添加到已有的 Cluster
                new_template_token_list = get_template(log_token_list, matched_cluster.template_token_list)
                matched_cluster.log_id_list.append(log_id)
                if ' '.join(new_template_token_list) != ' '.join(matched_cluster.template_token_list):
                    matched_cluster.template_token_list = new_template_token_list

                cluster_template_id = matched_cluster.template_id

            event_id_list.append(log_sig * 100 + cluster_template_id)

            count = idx + 1
            if count % 1000 == 0 or count == len(self.df_log):
                print('Processed {0:.1f}% of log lines.'.format(count * 100.0 / len(self.df_log)))

        self.outputEventId(event_id_list)
        # self.outputResult(all_cluster_list)
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
