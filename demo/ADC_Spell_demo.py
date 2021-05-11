import os
from logparser import evaluator
import logparser.ADC.ADC_Spell as ADC_Spell
from benchmark.ADC_Spell_benchmark import benchmark_settings

# The input directory of log file
output_dir = 'ADC_Spell_result/'  # The output directory of parsing results
one_setting = benchmark_settings['Proxifier']
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))

parser = ADC_Spell.LogParser(
    indir=input_dir,
    outdir=output_dir,
    log_format=one_setting['log_format'],
    tau=one_setting['tau'],
    rex=one_setting['regex']
)

parser.parse(log_file)

F1_measure, accuracy = evaluator.evaluate(
    groundtruth=os.path.join(input_dir, log_file + '_structured.csv'),
    parsedresult=os.path.join(output_dir, log_file + '_structured.csv'),
)

print(F1_measure, accuracy)
