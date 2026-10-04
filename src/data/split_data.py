import numpy as np
import pandas as pd

def split_data(clean, output):
    # Exact equality grouping (not a hash-only approximation), including missing values.
    groups=clean.groupby(list(clean.columns),dropna=False,sort=False).ngroup()
    meta=pd.DataFrame({'group':groups,'target':clean.heart_disease.astype(int)}).groupby('group').agg(target=('target','first'),size=('target','size'))
    rng=np.random.default_rng(42)
    assigned={}
    for target in [0,1]:
        subset=meta[meta.target==target]
        desired=np.array([.70,.15,.15])*subset['size'].sum()
        counts=np.zeros(3)
        # Randomized equal-record groups; largest groups first limits allocation error.
        order=rng.permutation(subset.index.to_numpy())
        order=sorted(order,key=lambda g:-int(meta.loc[g,'size']))
        for g in order:
            dest=int(np.argmax(desired-counts))
            assigned[g]=dest
            counts[dest]+=int(meta.loc[g,'size'])
    destinations=groups.map(assigned)
    splits={name:clean.loc[destinations==i] for i,name in enumerate(['train','validation','test'])}
    ids=[set(x.index) for x in splits.values()]
    assert not(ids[0]&ids[1] or ids[0]&ids[2] or ids[1]&ids[2])
    assert set.union(*ids)==set(clean.index)
    group_sets=[set(groups.loc[x.index]) for x in splits.values()]
    assert not(group_sets[0]&group_sets[1] or group_sets[0]&group_sets[2] or group_sets[1]&group_sets[2])
    membership=pd.DataFrame({'source_row_id':clean.index,'equality_group':groups.to_numpy(),'split':destinations.map({0:'train',1:'validation',2:'test'}).to_numpy()})
    membership.to_csv(output/'split_membership.csv',index=False)
    for name,df in splits.items(): df.to_csv(output/f'{name}.csv',index=False)
    return splits
