from logparser import evaluator
from logparser.ADC import ADC_Fast as ADC

from benchmark.ADC_New_benchmark import CONFIG_DICT
from logparser.utils.dataset import *

dataset = DATASET.Android

parser = ADC.LogParser(
    in_path='/media/zhixin/mydoc/PyCharm/logparser/logs/Android/Android_50m.log',
    dataset=dataset,
    rex=CONFIG_DICT[dataset].rex,
    st=CONFIG_DICT[dataset].st,
    pre=CONFIG_DICT[dataset].pre
)

time_elapsed, out_path = parser.parse()

# F1_measure, accuracy = evaluator.evaluate(
#     groundtruth=log_path_structured(dataset),
#     parsedresult=out_path
# )
#
# print(F1_measure, accuracy, time_elapsed.total_seconds())
