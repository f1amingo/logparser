import collections
import os
import pandas as pd
from benchmark.Lenma_benchmark import benchmark_settings
from logparser import LenMa
from File_Info import get_file_size

dataset = 'BGL'

output_dir = 'LenMa_result/'  # The output directory of parsing results
one_setting = benchmark_settings[dataset]
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))

file_size = get_file_size(dataset)

results = collections.defaultdict(list)
for size, file in file_size.items():
    parser = LenMa.LogParser(
        input_dir,
        output_dir,
        log_format=one_setting['log_format'],
        threshold=one_setting['threshold'],
        rex=one_setting['regex'],
    )
    time_elapsed = parser.parse(file)
    results['size'].append(size)
    results['time'].append(time_elapsed.total_seconds())
    print(results['time'])
    pd.DataFrame(results).to_csv('./LenMa_%s.csv' % dataset)
