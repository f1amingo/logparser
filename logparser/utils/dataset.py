'''
util for file path and log format
'''
from enum import Enum, unique
import os
import pandas as pd


@unique
class DATASET(Enum):
    Android = 'Android'
    Apache = 'Apache'
    BGL = 'BGL'
    Hadoop = 'Hadoop'
    HDFS = 'HDFS'
    HealthApp = 'HealthApp'
    HPC = 'HPC'
    Linux = 'Linux'
    Mac = 'Mac'
    OpenSSH = 'OpenSSH'
    OpenStack = 'OpenStack'
    Proxifier = 'Proxifier'
    Spark = 'Spark'
    Thunderbird = 'Thunderbird'
    Windows = 'Windows'
    Zookeeper = 'Zookeeper'


LOG_FORMAT = {
    DATASET.Android: '<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>',
    DATASET.Apache: '\[<Time>\] \[<Level>\] <Content>',
    DATASET.BGL: '<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>',
    DATASET.Hadoop: '<Date> <Time> <Level> \[<Process>\] <Component>: <Content>',
    DATASET.HDFS: '<Date> <Time> <Pid> <Level> <Component>: <Content>',
    DATASET.HealthApp: '<Time>\|<Component>\|<Pid>\|<Content>',
    DATASET.HPC: '<LogId> <Node> <Component> <State> <Time> <Flag> <Content>',
    DATASET.Linux: '<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>',
    DATASET.Mac: '<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>',
    DATASET.OpenSSH: '<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>',
    DATASET.OpenStack: '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>',
    DATASET.Proxifier: '\[<Time>\] <Program> - <Content>',
    DATASET.Spark: '<Date> <Time> <Level> <Component>: <Content>',
    DATASET.Thunderbird: '<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>',
    DATASET.Windows: '<Date> <Time>, <Level>                  <Component>    <Content>',
    DATASET.Zookeeper: '<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>',
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def log_path_structured(dataset: DATASET):
    file_name = '%s_2k.log_structured.csv' % dataset.value
    return os.path.join(PROJECT_DIR, 'logs', dataset.value, file_name)


def log_path_raw(dataset: DATASET):
    file_name = '%s_2k.log' % dataset.value
    return os.path.join(PROJECT_DIR, 'logs', dataset.value, file_name)


def log_path_template(dataset: DATASET):
    file_name = '%s_2k.log_templates.csv' % dataset.value
    return os.path.join(PROJECT_DIR, 'logs', dataset.value, file_name)


if __name__ == '__main__':
    for dataset in DATASET:
        print(dataset)
        pd.read_csv(log_path_structured(dataset))
    print('Passed all test cases.')
