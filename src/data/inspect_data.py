"""Complete, pre-cleaning raw dataset profile without a full-data copy."""
import pandas as pd
from .mappings import VARIABLES

def inspect_data(df, out):
    out.mkdir(parents=True, exist_ok=True)
    n=len(df)
    profile=[]
    for c in df:
        s=df[c]
        profile.append(dict(column=c,dtype=str(s.dtype),memory_bytes=int(s.memory_usage(index=False,deep=True)),missing_count=int(s.isna().sum()),missing_percentage=float(s.isna().mean()*100),unique_count=int(s.nunique(dropna=True))))
    p=pd.DataFrame(profile)
    p.to_csv(out/'column_profile.csv',index=False)
    p[['column','missing_count','missing_percentage']].to_csv(out/'missing_values.csv',index=False)
    duplicates=int(df.duplicated().sum())
    summary=dict(rows=n,columns=len(df.columns),memory_bytes=int(df.memory_usage(deep=True).sum()),duplicated_rows=duplicates)
    pd.DataFrame([summary]).to_csv(out/'dataset_summary.csv',index=False)
    (out/'duplicate_report.txt').write_text(f'Exact complete-row duplicates beyond first occurrence: {duplicates}\nRaw duplicates are reported, not automatically removed.\n')
    distributions=[]
    for c in [*VARIABLES,'_MICHD']:
        if c not in df: raise ValueError(f'Requested variable missing: {c}; no substitution permitted')
        counts=df[c].value_counts(dropna=False).rename_axis('original_value').reset_index(name='count')
        counts['percentage']=counts['count']/n*100
        counts.insert(0,'variable',c)
        if c=='_MICHD': counts.to_csv(out/'target_distribution.csv',index=False)
        else: distributions.append(counts)
    pd.concat(distributions).to_csv(out/'candidate_feature_distributions.csv',index=False)
    (out/'data_profile.md').write_text(f'# Complete raw profile\n\nRows: {n:,}; columns: {len(df.columns)}. Deep pandas memory: {summary["memory_bytes"]:,} bytes. Exact raw duplicates: {duplicates}.\n\nAll original names, datatypes, per-column memory, missing counts/percentages and nonmissing unique counts appear in column_profile.csv. Frequency CSVs include missing values and percentages over all raw rows. These raw counts do not decode response codes.\n\nTarget frequencies:\n\n```text\n'+df['_MICHD'].value_counts(dropna=False).to_string()+'\n```\n\nMost incomplete raw columns (often optional modules, not ordinary item nonresponse):\n\n```text\n'+p.sort_values('missing_percentage',ascending=False).head(15)[['column','missing_count','missing_percentage']].to_string(index=False)+'\n```\n\nCandidate raw missingness (does not yet include coded unknown/refused responses):\n\n```text\n'+p[p.column.isin(VARIABLES)][['column','missing_count','missing_percentage']].to_string(index=False)+'\n```\n\nNo automatic raw duplicate removal. Missing raw target rows are not usable for supervised learning. Documented response-code missingness is analyzed separately in reports/missingness_analysis.md.\n\nOriginal column names:\n\n'+', '.join(df.columns)+'\n',encoding='utf-8')
    return summary
