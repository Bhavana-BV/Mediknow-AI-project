import pathlib, sqlite3, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
ROOT=pathlib.Path(__file__).resolve().parents[1]

def normalize_query(query):
    q=query.lower()
    for old,new in (("paracetamol","acetaminophen"),("acetaminophen","acetaminophen"),("hypertension","high blood pressure")):
        q=re.sub(r"\b"+old+r"\b",new,q)
    q=re.sub(r"\b(what|which|is|are|does|do|tell|me|about|the|a|an|of|for|to|with|common|associated|particular|medicine|drug|used|use|can|there|any)\b"," ",q)
    return re.sub(r"\s+"," ",q).strip() or query

def retrieve(query, kind=None, threshold=0.06, required_section=None):
    db=ROOT/"data"/"mediknow.sqlite"
    if not db.exists(): return None
    con=sqlite3.connect(db); con.row_factory=sqlite3.Row
    sql="SELECT * FROM knowledge"; args=[]
    if kind in ("drug","disease"): sql+=" WHERE kind=?"; args.append(kind)
    if required_section:
        sql += (" AND " if args else " WHERE ")+"lower(text) LIKE ?"
        args.append("%"+required_section.lower()+"%")
    rows=con.execute(sql,args).fetchall(); con.close()
    if not rows:return None
    docs=[r["text"] for r in rows]
    titles=[r["name"] for r in rows]
    vec=TfidfVectorizer(stop_words="english",ngram_range=(1,2),sublinear_tf=True)
    matrix=vec.fit_transform(docs+titles+[normalize_query(query)]); q=matrix[-1]
    scores=cosine_similarity(q,matrix[:len(docs)]).ravel()
    title_scores=cosine_similarity(q,matrix[len(docs):len(docs)+len(titles)]).ravel()
    scores=0.35*scores+0.65*title_scores
    i=int(scores.argmax())
    return dict(rows[i]) if scores[i]>=threshold else None

def answer(query, intent):
    kind="disease" if intent=="disease_information" else "drug" if intent in ("drug_information","side_effects","precautions","drug_disease_relationship") else None
    required={"side_effects":"adverse reactions:","precautions":"warnings:","drug_disease_relationship":"indications and usage:"}.get(intent)
    hit=retrieve(query,kind,required_section=required)
    if not hit:return "I couldn't find a sufficiently relevant record in this local knowledge base. Please consult a qualified healthcare professional or the linked authoritative sources.",None
    sections=[s.strip() for s in re.split(r"\n\n",hit["text"]) if s.strip()]
    if intent=="side_effects": sections=["FDA label section (adverse reactions; this list is not a ranking of commonness): "+s.split(":",1)[1].strip() for s in sections if s.lower().startswith("adverse reactions:")]
    if intent=="precautions": sections=[s for s in sections if s.lower().startswith(("warnings:","precautions:"))]
    if intent=="drug_disease_relationship": sections=[s for s in sections if s.lower().startswith("indications and usage:")]
    if not sections:return "The retrieved record does not contain that specific section, so I won't infer an answer. Check the source label directly.",hit
    return "\n\n".join(sections),hit
