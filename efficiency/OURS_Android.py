import collections
from logparser.ADC import ADC_Fast as ADC
from benchmark.ADC_New_benchmark import CONFIG_DICT
from logparser.utils.dataset import *

dataset = DATASET.BGL

file_size = {
    '1m': '/media/zhixin/mydoc/PyCharm/logparser/logs/%s/%s_1m.log' % (dataset.value, dataset.value),
    '5m': '/media/zhixin/mydoc/PyCharm/logparser/logs/%s/%s_5m.log' % (dataset.value, dataset.value),
    '10m': '/media/zhixin/mydoc/PyCharm/logparser/logs/%s/%s_10m.log' % (dataset.value, dataset.value),
    '25m': '/media/zhixin/mydoc/PyCharm/logparser/logs/%s/%s_25m.log' % (dataset.value, dataset.value),
    '50m': '/media/zhixin/mydoc/PyCharm/logparser/logs/%s/%s_50m.log' % (dataset.value, dataset.value),
    '75m': '/media/zhixin/mydoc/PyCharm/logparser/logs/%s/%s_75m.log' % (dataset.value, dataset.value),
    '100m': '/media/zhixin/mydoc/PyCharm/logparser/logs/%s/%s_100m.log' % (dataset.value, dataset.value),
}

results = collections.defaultdict(list)
for size, file in file_size.items():
    parser = ADC.LogParser(
        in_path=file,
        dataset=dataset,
        rex=CONFIG_DICT[dataset].rex,
        st=CONFIG_DICT[dataset].st,
        pre=CONFIG_DICT[dataset].pre
    )
    time_elapsed, out_path = parser.parse()
    results['size'].append(size)
    results['time'].append(time_elapsed.total_seconds())
    print(results['time'])
    pd.DataFrame(results).to_csv('./OURS_%s.csv' % (dataset.value))
