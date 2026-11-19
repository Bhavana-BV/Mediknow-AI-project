"""Descriptive summaries and exploratory figures from the generated SQLite sample."""
import json, pathlib, sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    con=sqlite3.connect(ROOT/"data"/"mediknow.sqlite")
    df=pd.read_sql_query("SELECT kind,name,source,length(text) AS text_chars FROM knowledge",con); con.close()
    (ROOT/"reports").mkdir(exist_ok=True)
    summary={"record_count":int(len(df)),"records_by_kind":{str(k):int(v) for k,v in df.kind.value_counts().items()},
      "records_by_source":{str(k):int(v) for k,v in df.source.value_counts().items()},
      "unique_names_by_kind":{str(k):int(v) for k,v in df.groupby("kind").name.nunique().items()},
      "text_length_chars":{"mean":float(df.text_chars.mean()),"median":float(df.text_chars.median()),"min":int(df.text_chars.min()),"max":int(df.text_chars.max())},
      "caveat":"API query sample only; counts reflect records retrieved in this run, not real-world prevalence or complete source coverage."}
    (ROOT/"reports"/"dataset_summary.json").write_text(json.dumps(summary,indent=2))
    fig,ax=plt.subplots(figsize=(7,4)); sns.countplot(data=df,x="kind",hue="kind",legend=False,ax=ax,palette="Set2"); ax.set(title="Retrieved records by type",xlabel="Record type",ylabel="Record count"); fig.tight_layout(); fig.savefig(ROOT/"reports"/"figures"/"record_type_distribution.png",dpi=160); plt.close(fig)
    for kind in ("drug","disease"):
        top=df[df.kind==kind].name.value_counts().head(12).sort_values()
        fig,ax=plt.subplots(figsize=(9,5)); top.plot.barh(ax=ax,color="#507da5"); ax.set(title=f"Most frequent retrieved {kind} record names",xlabel="Records in this API sample",ylabel="Record name"); fig.tight_layout(); fig.savefig(ROOT/"reports"/"figures"/f"{kind}_record_distribution.png",dpi=160); plt.close(fig)
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
