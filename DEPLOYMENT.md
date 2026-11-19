# Hosting the Streamlit app

## Ready-to-deploy files

The entrypoint is `app.py`. The deployment bundle includes the trained intent model and pinned dependencies in `requirements.txt`. Raw downloaded JSON, SQLite's source-text snapshot, the local virtual environment, and scratch files are excluded by `.gitignore`. If the database is missing, the app downloads the small sample from FDA openFDA and MedlinePlus on first startup and builds a local SQLite database for that app instance. No API keys or Streamlit secrets are required.

## Streamlit Community Cloud

Community Cloud deploys from a GitHub repository. Create a GitHub repository, add this project directory's files, then sign in to [Streamlit Community Cloud](https://share.streamlit.io) with GitHub and create an app using:

* Repository: the GitHub repository you created
* Branch: `main` (or your chosen default branch)
* App file path: `app.py`
* Python version: 3.12, matching the environment used to train the saved scikit-learn model

The project has **not** been connected to GitHub or published from this workspace. Choose repository/app visibility deliberately before publishing. Streamlit's current documented workflow requires a GitHub repository and repository admin access. A public repository/app is viewable by anyone; a private app may have account limitations on the free Community Cloud plan. The deployed app retrieves short source passages at runtime, displays attribution and links, and does not put downloaded source snapshots into the public repository. Review [openFDA terms](https://open.fda.gov/terms/) and [MedlinePlus content-use guidance](https://medlineplus.gov/about/using/usingcontent/) before redistributing or modifying source text.

## Local production-like launch

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app performs no external API calls at runtime. Answers are limited to the included snapshot database, and every retrieved record links back to its source.
