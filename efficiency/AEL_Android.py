import collections
import os
import pandas as pd
from benchmark.AEL_benchmark import benchmark_settings
from logparser import AEL
from File_Info import get_file_size

dataset = 'BGL'

output_dir = 'AEL_result/'  # The output directory of parsing results
one_setting = benchmark_settings[dataset]
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))

file_size = get_file_size(dataset)

results = collections.defaultdict(list)
for size, file in file_size.items():
    parser = AEL.LogParser(
        input_dir,
        output_dir,
        log_format=one_setting['log_format'],
        rex=one_setting['regex'],
        minEventCount=one_setting['minEventCount'],
        merge_percent=one_setting['merge_percent'],
        keep_para=False
    )
    time_elapsed = parser.parse(file)
    results['size'].append(size)
    results['time'].append(time_elapsed.total_seconds())
    print(results['time'])
    pd.DataFrame(results).to_csv('./AEL_%s.csv' % dataset)
