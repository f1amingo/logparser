"""
签名算法的正确性
1. 一定不会把同类型日志分到不同桶中
Android E10 E108
tag="RILJ_ACK_WL"
tag="*launch*"
tag="View Lock"

Mac E208
en0: channel changed to 1
en0: channel changed to 132,+1

Mac E267
network changed: v4(en0-:10.105.163.202) v6(en0:2607:f140:6000:8:c6b3:1ff:fecd:467f) DNS! Proxy SMB
network changed: v4(en0:10.105.160.237) v6(en0!:2607:f140:6000:8:f1dc:a608:863:19ad) DNS Proxy SMB
network changed: v4(en0+:10.105.160.226) v6(en0:2607:f140:6000:8:c6b3:1ff:fecd:467f) DNS! Proxy SMB

Android E41
Surface(name=InputMethod)
Surface(name=PopupWindow:9b04807)
Surface(name=com.tencent.qt.qtl/com.tencent.video.player.activity.PlayerActivity)
"""

import pandas as pd
from logparser.utils.dataset import *
import collections
from logparser.ADC import log_signature

if __name__ == '__main__':
    result_dict = collections.defaultdict(list)
    for dataset in DATASET:
        print(dataset)
        # if dataset != DATASET.Android:
        #     continue
        eventId_signature = collections.defaultdict()
        df = pd.read_csv(log_path_structured(dataset))
        for idx, row in df.iterrows():
            content = row['Content']
            eventId = row['EventId']
            template = row['EventTemplate']
            sig = log_signature(content)
            if eventId not in eventId_signature:
                eventId_signature[eventId] = sig
            else:
                if eventId_signature[eventId] != sig:
                    result_dict['dataset'].append(dataset.value)
                    result_dict['eventId'].append(eventId)
                    result_dict['signature'].append(sig)
                    result_dict['content'].append(content)
                    result_dict['template'].append(template)

    pd.DataFrame(result_dict).to_csv('%s.csv' % os.path.basename(__file__), index=False)
