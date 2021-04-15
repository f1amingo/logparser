'''
util for file path
'''
from enum import Enum, unique
import os


@unique
class DATASET(Enum):
    HDFS = 'HDFS'
    Hadoop = 'Hadoop'
    Spark = 'Spark'
    Zookeeper = 'Zookeeper'
    BGL = 'BGL'
    HPC = 'HPC'
    Thunderbird = 'Thunderbird'
    Windows = 'Windows'
    Linux = 'Linux'
    Android = 'Andriod'  # todo rename
    Apache = 'Apache'
    HealthApp = 'HealthApp'
    Proxifier = 'Proxifier'
    OpenSSH = 'OpenSSH'
    OpenStack = 'OpenStack'
    Mac = 'Mac'


def path_structured(dataset: DATASET):
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    file_name = '%s_2k.log_structured.csv' % dataset.value
    return os.path.join(parent_dir, dataset.value, file_name)


def path_raw(dataset: DATASET):
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    file_name = '%s_2k.log' % dataset.value
    return os.path.join(parent_dir, dataset.value, file_name)
