import os
from logparser import evaluator
# from logparser import ADC
import logparser.ADC.ADC_Drain as Drain
# import logparser.ADC.ADC_Spell as Spell

input_dir = '../logs/HDFS_/'  # The input directory of log file
output_dir = 'ADC_result/'  # The output directory of parsing results
log_file = 'HDFS_2k.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS_ log format
minEventCount = 2  # The minimum number of events in a bin
merge_percent = 0.5  # The percentage of different tokens
# match blockId and IP(10.251.110.8:50010)
regex = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?']  # Regular expression list for optional preprocessing (default: [])

# parser = Drain.LogParser(input_dir, output_dir, log_format, rex=regex, keep_para=False,
#                        minEventCount=minEventCount, merge_percent=merge_percent)

# ADC_Drain
parser = Drain.LogParser(log_format, indir=input_dir, outdir=output_dir, depth=4, st=0.5, rex=regex)

# ADC_Spell
# parser = Spell.LogParser(indir=input_dir, outdir=output_dir, log_format=log_format, tau=0.5, rex=[])

parser.parse(log_file)

F1_measure, accuracy = evaluator.evaluate(
    groundtruth=os.path.join(input_dir, log_file + '_structured.csv'),
    parsedresult=os.path.join(output_dir, log_file + '_structured.csv'),
)
print(F1_measure, accuracy)
