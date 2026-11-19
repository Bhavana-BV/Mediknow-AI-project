import sqlite3, joblib, streamlit as st
from src.retrieval import answer, ROOT
st.set_page_config(page_title="MediKnow AI",page_icon="🩺",layout="wide")
st.title("MediKnow AI")
st.caption("Educational drug and disease information assistant, grounded in linked source records.")
st.warning("Not for diagnosis or treatment. Do not use this tool to start, stop, or change medication. Seek medical advice from a qualified professional.")
model_path=ROOT/"models"/"intent_model.joblib"; db=ROOT/"data"/"mediknow.sqlite"
if not model_path.exists(): st.info("Set up the project and train the intent model first. See README.md → Quick start."); st.stop()
if not db.exists():
    with st.spinner("Loading the public FDA and MedlinePlus sample records for this app instance..."):
        try:
            from src.build_data import main as download_drug_records
            from src.prepare_database import main as prepare_knowledge_base
            download_drug_records()
            prepare_knowledge_base()
        except Exception as exc:
            st.error("The source data could not be fetched. Please reload later or consult the README setup steps.")
            st.stop()
model=joblib.load(model_path)
page=st.sidebar.radio("Explore",["Home","AI chatbot","Drug information","Disease information","Knowledge explorer","Search history","About"])
if "history" not in st.session_state: st.session_state.history=[]
def run_query(q):
    intent=model.predict([q])[0]; text,source=answer(q,intent); st.session_state.history.append((q,intent))
    st.markdown("**Predicted query category:** "+intent.replace("_"," ")); st.write(text)
    if source: st.caption(f"Record: {source['name']} · Source: {source['source']} · Retrieved (UTC): {source['retrieved_utc']}"); st.markdown(f"[Open source record]({source['source_url']})")
if page=="Home":
    st.subheader("Ask about a medicine or health topic")
    st.write("Try: What is diabetes? · What are common side effects of ibuprofen? · What precautions are in the label for metformin?")
    st.write("Answers are limited to records available locally. Citations open the underlying source.")
elif page=="AI chatbot":
    q=st.text_input("Your question",placeholder="What is diabetes?")
    if st.button("Search",type="primary") and q.strip(): run_query(q)
elif page in ("Drug information","Disease information"):
    q=st.text_input("Search term or question")
    if st.button("Find information") and q.strip(): run_query(q)
elif page=="Knowledge explorer":
    if db.exists():
        con=sqlite3.connect(db); data=con.execute("SELECT kind,name,source,source_url FROM knowledge ORDER BY kind,name").fetchall(); con.close()
        st.dataframe(data,use_container_width=True,column_config={"source_url":st.column_config.LinkColumn("Reference")})
    else: st.info("Knowledge base not built yet. Follow the README setup commands.")
elif page=="Search history":
    if st.session_state.history: st.dataframe([{"question":q,"predicted category":i} for q,i in reversed(st.session_state.history)],use_container_width=True)
    else: st.write("No searches in this session yet.")
elif page=="About":
    st.subheader("About this educational project")
    st.write("The intent classifier compares TF-IDF with Logistic Regression, Multinomial Naive Bayes, and Linear SVM. Answers use TF-IDF similarity over a small SQLite knowledge base built from FDA labeling and MedlinePlus health topics.")
    st.write("The starter classifier corpus is small and hand-authored for a classroom demonstration. It must not be treated as a validated medical language model.")
