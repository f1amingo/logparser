import os
from logparser import evaluator
from benchmark.Drain_benchmark import benchmark_settings
import logparser.ADC.ADC_Drain as Drain

# from logparser import ADC
# import logparser.ADC.ADC_Spell as Spell
# from benchmark.Spell_benchmark import benchmark_settings

# The input directory of log file
output_dir = 'ADC_result/'  # The output directory of parsing results
one_setting = benchmark_settings['Proxifier']
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))

# parser = Drain.LogParser(input_dir, output_dir, log_format, rex=regex, keep_para=False,
#                        minEventCount=minEventCount, merge_percent=merge_percent)

# ADC_Drain
parser = Drain.LogParser(
    log_format=one_setting['log_format'],
    indir=input_dir,
    outdir=output_dir,
    depth=one_setting['depth'],
    st=one_setting['st'],
    rex=one_setting['regex']
)

# ADC_Spell
# parser = Spell.LogParser(
#     indir=input_dir,
#     outdir=output_dir,
#     log_format=one_setting['log_format'],
#     tau=one_setting['tau'],
#     rex=one_setting['regex']
# )

parser.parse(log_file)

F1_measure, accuracy = evaluator.evaluate(
    groundtruth=os.path.join(input_dir, log_file + '_structured.csv'),
    parsedresult=os.path.join(output_dir, log_file + '_structured.csv'),
)

print(F1_measure, accuracy)
