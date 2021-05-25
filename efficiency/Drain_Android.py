import collections
import os
import pandas as pd
from benchmark.Drain_benchmark import benchmark_settings
from logparser import Drain
from File_Info import get_file_size

# dataset = 'Android'
dataset = 'BGL'

output_dir = 'Drain_result/'  # The output directory of parsing results
one_setting = benchmark_settings[dataset]
log_file = os.path.basename(one_setting['log_file'])
input_dir = os.path.join('../logs/', os.path.dirname(one_setting['log_file']))

file_size = get_file_size(dataset)

results = collections.defaultdict(list)
for size, file in file_size.items():
    parser = Drain.LogParser(
        log_format=one_setting['log_format'],
        indir=input_dir,
        outdir=output_dir,
        depth=one_setting['depth'],
        st=one_setting['st'],
        rex=one_setting['regex'],
        keep_para=False
    )
    time_elapsed = parser.parse(file)
    results['size'].append(size)
    results['time'].append(time_elapsed.total_seconds())
    print(results['time'])
    pd.DataFrame(results).to_csv('./Drain_%s.csv' % dataset)
