import os
import time

from logparser import evaluator
from benchmark.AEL_benchmark import benchmark_settings
from logparser import AEL

output_dir = 'AEL_result/'  # The output directory of parsing results
one_setting = benchmark_settings['Hadoop']
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))
parser = AEL.LogParser(
    input_dir,
    output_dir,
    one_setting['log_format'],
    rex=one_setting['regex'],
    minEventCount=one_setting['minEventCount'],
    merge_percent=one_setting['merge_percent'])

parser.parse(log_file)

start = time.perf_counter()
parser.parse(log_file)
end = time.perf_counter()

F1_measure, accuracy = evaluator.evaluate(
    groundtruth=os.path.join(input_dir, log_file + '_structured.csv'),
    parsedresult=os.path.join(output_dir, log_file + '_structured.csv'),
)

print(F1_measure, accuracy)
print(end - start)
