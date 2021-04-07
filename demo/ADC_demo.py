<<<<<<< HEAD
import sys

sys.path.append('../')
from logparser import ADC

input_dir = '../logs/HDFS/'  # The input directory of log file
output_dir = 'ADC_result/'  # The output directory of parsing results
log_file = 'HDFS_2k.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
minEventCount = 2  # The minimum number of events in a bin
merge_percent = 0.5  # The percentage of different tokens
# match blockId and IP(10.251.110.8:50010)
regex = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?']  # Regular expression list for optional preprocessing (default: [])

parser = ADC.LogParser(input_dir, output_dir, log_format, rex=regex, keep_para=False,
                       minEventCount=minEventCount, merge_percent=merge_percent)
parser.parse(log_file)
=======
import sys

sys.path.append('../')
from logparser import ADC

input_dir = '../logs/HDFS/'  # The input directory of log file
output_dir = 'ADC_result/'  # The output directory of parsing results
log_file = 'HDFS_2k.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
minEventCount = 2  # The minimum number of events in a bin
merge_percent = 0.5  # The percentage of different tokens
# match blockId and IP(10.251.110.8:50010)
regex = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?']  # Regular expression list for optional preprocessing (default: [])

parser = ADC.LogParser(input_dir, output_dir, log_format, rex=regex, keep_para=False,
                       minEventCount=minEventCount, merge_percent=merge_percent)
parser.parse(log_file)
>>>>>>> ef98b6dc1ee508ff3a82c9b14e7856626069661c
