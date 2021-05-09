import collections
import pandas as pd
from typing import List


class LogCluster:
    # LogCluster keeps a list of template with the same signature
    def __init__(self, template_list: List):
        self.template_token_list = template_list


class LogParser:
    def __init__(self, **kwargs):
        self.log_format = kwargs['log_format']
        self.indir = kwargs['indir']
        self.outdir = kwargs['outdir']

        self.rex = kwargs['rex']
        self.st = kwargs['st']
        self.keep_para = kwargs['keep_para']

        self.log_name = None
        self.df_log = None
        self.log_cluster_dict = None

    def parse(self):
        self.load_data(self.indir)
        self.log_cluster_dict = collections.defaultdict(LogCluster)

        # 遍历每一行
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
        self.dump_result(self.outdir)

    def load_data(self, filepath: str) -> pd.DataFrame:
        pass

    def preprocess(self, log_content: str) -> str:
        pass

    def split(self, log_content: str) -> List[str]:
        pass

    def calc_signature(self, token_list: List[str]) -> int:
        pass

    def search(self, log_cluster: LogCluster, token_list: List[str]) -> (int, List[str]):
        pass

    def add_template(self, log_cluster: LogCluster, token_list: List[str]) -> int:
        pass

    def new_template_from(self, log_token_list: List[str], template_token_list: List[str]) -> List[str]:
        pass

    def update_template(self, log_cluster: LogCluster, token_list: List[str], idx: int):
        pass

    def dump_result(self, out_path: str):
        pass
