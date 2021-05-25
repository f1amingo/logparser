import collections
from logparser import evaluator
from logparser.ADC import ADC_New
from logparser.utils.dataset import *


class ADCConfig:
    def __init__(self):
        self.rex = []
        self.st = 0.5
        self.pre = 1


CONFIG_DICT = collections.defaultdict(ADCConfig)

CONFIG_DICT[DATASET.Android].rex = [
    # r'(/[\w-]+)+',
    r'([\w-]+\.){2,}[\w-]+',
    # r'\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b'
]
CONFIG_DICT[DATASET.Android].st = 0.1
CONFIG_DICT[DATASET.Android].pre = 5

# CONFIG_DICT[DATASET.Apache].rex = [r'(\d+\.){3}\d+']

# CONFIG_DICT[DATASET.BGL].rex = [r'core\.\d+']
CONFIG_DICT[DATASET.BGL].st = 0.5
CONFIG_DICT[DATASET.BGL].pre = 4  # vital

# CONFIG_DICT[DATASET.Hadoop].rex = [r'(\d+\.){3}\d+']
CONFIG_DICT[DATASET.Hadoop].st = 0.1
CONFIG_DICT[DATASET.Hadoop].pre = 10

# CONFIG_DICT[DATASET.HDFS].rex = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?']

CONFIG_DICT[DATASET.HealthApp].st = 0.1

# CONFIG_DICT[DATASET.HPC].rex = [r'=\d+']
CONFIG_DICT[DATASET.HPC].st = 0.1
CONFIG_DICT[DATASET.HPC].pre = 2

# CONFIG_DICT[DATASET.Linux].rex = [r'(\d+\.){3}\d+', r'\d{2}:\d{2}:\d{2}']
CONFIG_DICT[DATASET.Linux].st = 0.1

# CONFIG_DICT[DATASET.Mac].rex = [r'([\w-]+\.){2,}[\w-]+']
CONFIG_DICT[DATASET.Mac].pre = 100
CONFIG_DICT[DATASET.Mac].st = 0.1

# CONFIG_DICT[DATASET.OpenSSH].rex = [r'(\d+\.){3}\d+', r'([\w-]+\.){2,}[\w-]+']
CONFIG_DICT[DATASET.OpenSSH].pre = 2
CONFIG_DICT[DATASET.OpenSSH].st = 0.1

# vital: r'/.*"' r'((\d+\.){3}\d+,?)+'
# CONFIG_DICT[DATASET.OpenStack].rex = [r'/.*"', r'((\d+\.){3}\d+,?)+', r'/.+?\s']
CONFIG_DICT[DATASET.OpenStack].rex = [r'/.*"', r'((\d+\.){3}\d+,?)+']
CONFIG_DICT[DATASET.OpenStack].pre = 100

# CONFIG_DICT[DATASET.Proxifier].rex = [r'<\d+\ssec', r'([\w-]+\.)+[\w-]+(:\d+)?', r'\d{2}:\d{2}(:\d{2})*', '\s(\d+)\s']
CONFIG_DICT[DATASET.Proxifier].pre = 10
CONFIG_DICT[DATASET.Proxifier].st = 0.1

# CONFIG_DICT[DATASET.Spark].rex = [r'(\d+\.){3}\d+', r'\b[KGTM]?B\b', r'([\w-]+\.){2,}[\w-]+']
CONFIG_DICT[DATASET.Spark].st = 0.1

# vital: r'LOCAL\(0\)'
# CONFIG_DICT[DATASET.Thunderbird].rex = [r'(\d+\.){3}\d+', r'LOCAL\(0\)']
CONFIG_DICT[DATASET.Thunderbird].rex = [r'LOCAL\(0\)']
CONFIG_DICT[DATASET.Thunderbird].st = 0.5

# CONFIG_DICT[DATASET.Windows].rex = [r'0x.*?\s']
CONFIG_DICT[DATASET.Windows].pre = 7
CONFIG_DICT[DATASET.Windows].st = 0.1

# CONFIG_DICT[DATASET.Zookeeper].rex = [r'(/|)(\d+\.){3}\d+(:\d+)?']
CONFIG_DICT[DATASET.Zookeeper].st = 0.1
CONFIG_DICT[DATASET.Zookeeper].pre = 100

if __name__ == '__main__':
    benchmark_result = []

    for dataset in DATASET:
        print('\n=== Evaluation on %s ===' % dataset)

        parser = ADC_New.LogParser(
            dataset=dataset,
            rex=CONFIG_DICT[dataset].rex,
            st=CONFIG_DICT[dataset].st,
            pre=CONFIG_DICT[dataset].pre,
        )

        time_elapsed, out_path = parser.parse()

        F1_measure, accuracy = evaluator.evaluate(
            groundtruth=log_path_structured(dataset),
            parsedresult=out_path
        )
        benchmark_result.append([dataset, F1_measure, accuracy, time_elapsed.total_seconds()])

    print('\n=== Overall evaluation results ===')
    df_result = pd.DataFrame(benchmark_result, columns=['Dataset', 'F1_measure', 'Accuracy', 'Time'])
    df_result.set_index('Dataset', inplace=True)
    print(df_result)
    accuracy_list = list(map(str, list(df_result['Accuracy'])))
    print('\t'.join(accuracy_list))
    print('\t'.join(list(map(str, list(df_result['Time'])))))
    df_result.T.to_csv('ADC_New_benchmark_result.csv')
