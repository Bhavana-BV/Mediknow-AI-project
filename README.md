# MediKnow AI

An educational college mini-project for classifying medicine and disease questions and retrieving relevant passages from linked public health sources. It is not a diagnostic or treatment system.

## Quick start (Windows PowerShell)

Install Python 3.10+ and ensure `py` is on PATH. From this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python src\build_data.py
python src\prepare_database.py
python src\analyze_data.py
python src\train_model.py
streamlit run app.py
```

The first step downloads a small live sample: up to ten labels for each of five generic drug-name searches from openFDA. Database preparation fetches up to five MedlinePlus health-topic search records for each of five disease queries. The exact sample is API-dependent and is not exhaustive. The commands need internet access. `data/raw/` stores downloaded JSON and `data/mediknow.sqlite` is generated locally.

## Project structure

```text
MediKnow-AI/
├── app.py                         Streamlit interface
├── requirements.txt
├── src/
│   ├── build_data.py              openFDA sample download
│   ├── prepare_database.py        MedlinePlus fetch + SQLite normalization
│   ├── intent_data.py             transparent starter query-intent examples
│   ├── train_model.py             TF-IDF + CV model comparison and figures
│   └── retrieval.py               local similarity search and safe fallback
├── data/{raw,processed}/          downloaded and prepared data
├── models/                        trained pipeline and classes
├── reports/                       metrics, comparison CSV, figures, project report
└── docs/                           architecture / flow diagrams
```

## Data, attributes, and permitted use

* **openFDA drug product labeling API**: `https://api.fda.gov/drug/label.json`; query fields include `openfda.generic_name`, `indications_and_usage`, `adverse_reactions`, `warnings`, and `precautions`. The download script keeps returned records as received. FDA notes that some records may contain copyrighted material supplied by third parties. Review [openFDA terms](https://open.fda.gov/terms/) before redistributing raw label text; retain attribution and use the source link. This sample is for educational analysis, not a complete or current clinical reference.
* **MedlinePlus Health Topics web service**: `https://wsearch.nlm.nih.gov/ws/query`; the script stores topic title, snippet and source URL. MedlinePlus content has mixed rights: some is public domain and some is copyrighted/licensed. Follow [MedlinePlus XML and data guidance](https://medlineplus.gov/xml.html) and [content use guidance](https://medlineplus.gov/about/using/usingcontent/); preserve MedlinePlus attribution and check licensing before reusing full text.
* Data is fetched when the user runs the scripts; this repository does not claim a particular snapshot date. The SQLite `retrieved_utc` field records local ingestion time in UTC. Always open the source link for current content.

### Cleaning and analysis

The normalization step extracts the available relevant FDA label sections and MedlinePlus title/snippet, skips absent fields, stores source attribution, and creates one SQLite knowledge table. The sample remains intentionally small. Duplicate MedlinePlus URLs are removed. Run analysis on the generated raw JSON in a notebook or extend `prepare_database.py`; do not interpret the deliberately limited drug queries as representative category distributions.

## Genuine ML component and evaluation

`src/intent_data.py` contains 30 visible, hand-authored example questions across five intents. It is a starter teaching corpus, not a collected user dataset. `train_model.py` uses a stratified 3-fold cross-validation split, with a fixed seed, TF-IDF unigram/bigram features, and compares Logistic Regression, Multinomial Naive Bayes, and Linear SVM. Each query is predicted out-of-fold for the reported comparison and confusion matrix, avoiding fitting the evaluated model on its own fold. Then the top weighted-F1 pipeline is refit on all examples and saved as `models/intent_model.joblib` for the demo.

The corpus is extremely small and templated. Cross-validation scores can be optimistic and do not show performance on real users or medical language. Grow and independently review a larger labeled set before making any quality claims. Metrics, class-level precision/recall/F1 and figures are generated only by running the training command; no values are prefilled or fabricated.

## Safety and known limits

The classifier selects an intent, then TF-IDF similarity selects a source record. It is extractive, not generative. If a matching label section is absent, it says so rather than filling gaps. Similarity thresholds and a small corpus can still select an irrelevant record; this prototype is not validated for care. It must never provide personalized dosage, diagnose, or tell a person to start/stop medication. Serious reactions or urgent symptoms warrant immediate professional/emergency help. For medical decisions, consult a qualified healthcare professional and the original source.

## Reproducible outputs

After running the commands, expect:

* `models/intent_model.joblib`, `models/intent_classes.json`
* `data/raw/openfda_drug_labels.json`, `data/raw/medlineplus_topics.json`, `data/mediknow.sqlite`
* `reports/model_comparison.csv`, `reports/model_metrics.json`
* `reports/dataset_summary.json`, `reports/figures/record_type_distribution.png`, drug and disease record charts
* `reports/figures/model_comparison.png`, `reports/figures/confusion_matrix.png`

See `docs/PROJECT_REPORT.md` for the report outline and architecture diagrams. Streamlit search history lasts for the current browser session only.

See [DEPLOYMENT.md](DEPLOYMENT.md) for Streamlit Community Cloud setup. The source folder is prepared, but it has not been published to a hosting account.

