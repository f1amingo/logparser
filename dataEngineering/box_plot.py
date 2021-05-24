import matplotlib.pyplot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# sns.boxplot(x="method", y="accuracy",
#             palette=["m", "g"],
#             data=data_df)


file_list = {
    'LenMa': '../benchmark/lock/Lenma_benchmark_result.csv',
    'Spell': '../benchmark/lock/Spell_benchmark_result.csv',
    'AEL': '../benchmark/lock/AEL_benchmark_result.csv',
    'IPLoM': '../benchmark/lock/IPLoM_benchmark_result.csv',
    'Drain': '../benchmark/lock/Drain_benchmark_result.csv',
    'LSF': '../benchmark/lock/ADC_New_benchmark_result.csv',
}

plot_data = {
    'method': [],
    'dataset': [],
    'accuracy': [],
}
for method, file in file_list.items():
    try:
        df = pd.read_csv(file)
        for col in df.iteritems():
            dataset = col[0]
            f1 = col[1][0]
            accuracy = col[1][1]
            if accuracy == 'Accuracy':
                continue
            plot_data['method'].append(method)
            plot_data['dataset'].append(dataset)
            plot_data['accuracy'].append(accuracy)
    except:
        print('result file not found for ', method)
        continue

sns.set_theme(style="ticks", palette="pastel")

data_df = pd.DataFrame(plot_data)

# boxplot_sorted(data_df, by=["method"], column="accuracy")

ax = sns.boxplot(x="method", y="accuracy",
                 palette="Spectral",
                 data=data_df)
ax.set(xlabel='', ylabel='Parsing Accuracy')

sns.color_palette("coolwarm", as_cmap=True)
# sns.despine(offset=10, trim=True)

plt.show()
