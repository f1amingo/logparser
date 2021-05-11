from logparser import evaluator
from logparser import ADC
from benchmark.ADC_benchmark import CONFIG_DICT
from logparser.utils.dataset import *

dataset = DATASET.Proxifier
parser = ADC.LogParser(
    dataset=dataset,
    rex=CONFIG_DICT[dataset].rex,
    st=CONFIG_DICT[dataset].st,
    pre=CONFIG_DICT[dataset].pre
)

out_path = parser.parse()

F1_measure, accuracy = evaluator.evaluate(
    groundtruth=log_path_structured(dataset),
    parsedresult=out_path
)

print(F1_measure, accuracy)
