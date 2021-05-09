import collections
from logparser import evaluator
from logparser.ADC import ADC
from logparser.utils.dataset import *


class ADCConfig:
    def __init__(self):
        self.rex = []
        self.st = 0.5
        self.pre = 1


CONFIG_DICT = collections.defaultdict(ADCConfig)
CONFIG_DICT[DATASET.Android].rex = [r'".*"']
CONFIG_DICT[DATASET.Android].pre = 3
CONFIG_DICT[DATASET.Apache]
CONFIG_DICT[DATASET.BGL].rex = [r'\d+']
CONFIG_DICT[DATASET.Hadoop].st = 0.4
CONFIG_DICT[DATASET.HDFS].rex = [r'(\d+\.){3}\d+(:\d+)?']
CONFIG_DICT[DATASET.HealthApp]
CONFIG_DICT[DATASET.HPC]
CONFIG_DICT[DATASET.Linux]
CONFIG_DICT[DATASET.Mac].st = 0.7
CONFIG_DICT[DATASET.Mac].rex = [r'([\w-]+\.){2,}[\w-]+']
CONFIG_DICT[DATASET.OpenSSH].st = 0.8
CONFIG_DICT[DATASET.OpenSSH].rex = [r'(\d+\.){3}\d+', r'([\w-]+\.){2,}[\w-]+']
CONFIG_DICT[DATASET.OpenStack]
CONFIG_DICT[DATASET.Proxifier]
CONFIG_DICT[DATASET.Spark]
CONFIG_DICT[DATASET.Thunderbird].st = 0.8
CONFIG_DICT[DATASET.Thunderbird].rex = [r'LOCAL\(0\)']
CONFIG_DICT[DATASET.Windows].st = 0.8
CONFIG_DICT[DATASET.Zookeeper]

if __name__ == '__main__':
    benchmark_result = []

    for dataset in DATASET:
        print('\n=== Evaluation on %s ===' % dataset)
        parser = ADC.LogParser(
            dataset=dataset,
            rex=CONFIG_DICT[dataset].rex,
            st=CONFIG_DICT[dataset].st,
            pre=CONFIG_DICT[dataset].pre,
        )

        out_path = parser.parse()

        F1_measure, accuracy = evaluator.evaluate(
            groundtruth=log_path_structured(dataset),
            parsedresult=out_path
        )
        benchmark_result.append([dataset, F1_measure, accuracy])

    print('\n=== Overall evaluation results ===')
    df_result = pd.DataFrame(benchmark_result, columns=['Dataset', 'F1_measure', 'Accuracy'])
    df_result.set_index('Dataset', inplace=True)
    print(df_result)
    accuracy_list = list(map(str, list(df_result['Accuracy'])))
    print('\t'.join(accuracy_list))
    df_result.T.to_csv('ADC_benchmark_result.csv')
