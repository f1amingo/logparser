import os
from logparser import evaluator
from benchmark.Drain_benchmark import benchmark_settings
from logparser import Drain

output_dir = 'Drain_result/'  # The output directory of parsing results
one_setting = benchmark_settings['Android']
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))

parser = Drain.LogParser(
    log_format=one_setting['log_format'],
    indir=input_dir,
    outdir=output_dir,
    depth=one_setting['depth'],
    st=one_setting['st'],
    rex=one_setting['regex']
)
parser.parse(log_file)

F1_measure, accuracy = evaluator.evaluate(
    groundtruth=os.path.join(input_dir, log_file + '_structured.csv'),
    parsedresult=os.path.join(output_dir, log_file + '_structured.csv'),
)

print(F1_measure, accuracy)
