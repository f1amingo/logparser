import pandas as pd

df = pd.read_csv('./logs/OpenStack/OpenStack_2k.log_structured.csv')
counter = {'E25': 0, "E32": 0}
for idx, row in df.iterrows():
    content = row['Content']
    eventId = row['EventId']
    if eventId in counter:
        counter[eventId] += 1
    # if content.find('=') > -1:
    #     print(eventId, content)
print(counter)
