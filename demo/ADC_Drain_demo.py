import os
from logparser import evaluator
from benchmark.ADC_Drain_benchmark import benchmark_settings
import logparser.ADC.ADC_Drain_Sim as ADC_Drain

# The input directory of log file
output_dir = 'ADC_Drain_result/'  # The output directory of parsing results
one_setting = benchmark_settings['Andriod']
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))

# ADC_Drain
parser = ADC_Drain.LogParser(
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
