"""Normalize downloaded FDA labels and MedlinePlus topic snippets into SQLite."""
import json, pathlib, sqlite3, xml.etree.ElementTree as ET, re
from html import unescape
import requests
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT/"data"/"mediknow.sqlite"
FDA = ROOT/"data"/"raw"/"openfda_drug_labels.json"
TOPICS = ROOT/"data"/"raw"/"medlineplus_topics.json"

def plain_text(value):
    value=unescape(value or "")
    value=re.sub(r"<[^>]*>"," ",value)
    return re.sub(r"\s+"," ",value).strip()

def download_topics():
    records=[]
    for term in ("diabetes", "hypertension", "asthma", "migraine", "arthritis"):
        r=requests.get("https://wsearch.nlm.nih.gov/ws/query",params={"db":"healthTopics","term":term,"retmax":5},timeout=45); r.raise_for_status()
        root=ET.fromstring(r.content)
        for doc in root.findall(".//document"):
            contents=doc.findall("./content")
            title=plain_text(contents[0].text) if contents else ""
            text=plain_text(" ".join(x.text or "" for x in contents))
            link=doc.attrib.get("url", "https://medlineplus.gov/")
            if title and not any(x["url"]==link for x in records): records.append({"title":title,"text":text,"url":link,"source":"MedlinePlus"})
    TOPICS.write_text(json.dumps(records,indent=2),encoding="utf-8")

def main():
    if not TOPICS.exists() or "--refresh" in sys.argv: download_topics()
    drugs=json.loads(FDA.read_text(encoding="utf-8")) if FDA.exists() else []
    topics=json.loads(TOPICS.read_text(encoding="utf-8"))
    con=sqlite3.connect(DB); con.execute("DROP TABLE IF EXISTS knowledge")
    con.execute("CREATE TABLE knowledge(id INTEGER PRIMARY KEY, kind TEXT, name TEXT, text TEXT, source TEXT, source_url TEXT, retrieved_utc TEXT)")
    for d in drugs:
        of=d.get("openfda",{}); names=of.get("generic_name",[]) or of.get("brand_name",[])
        name=(names[0] if names else "Drug label").title(); sections=[]
        for field,label in (("indications_and_usage","Indications and usage"),("adverse_reactions","Adverse reactions"),("warnings","Warnings"),("precautions","Precautions")):
            values=d.get(field,[])
            if values: sections.append(label+": "+" ".join(values)[:4000])
        if sections: con.execute("INSERT INTO knowledge(kind,name,text,source,source_url,retrieved_utc) VALUES(?,?,?,?,?,datetime('now'))",("drug",name,"\n\n".join(sections),"FDA openFDA drug labeling API","https://open.fda.gov/apis/drug/label/"))
    for t in topics: con.execute("INSERT INTO knowledge(kind,name,text,source,source_url,retrieved_utc) VALUES(?,?,?,?,?,datetime('now'))",("disease",t["title"],t["text"],"MedlinePlus",t["url"]))
    con.commit(); n=con.execute("SELECT count(*) FROM knowledge").fetchone()[0]; con.close()
    print(f"Created {DB} with {n} source-attributed records")
if __name__=="__main__": main()
