"""Train and compare intent models using stratified out-of-fold predictions."""
import json, pathlib, joblib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
    classification_report, ConfusionMatrixDisplay)
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from intent_data import TRAINING_EXAMPLES

ROOT = pathlib.Path(__file__).resolve().parents[1]
def main():
    df = pd.DataFrame(TRAINING_EXAMPLES, columns=["query", "intent"])
    X, y = df["query"], df["intent"]
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    candidates = {"Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
                  "Multinomial Naive Bayes": MultinomialNB(), "Linear SVM": LinearSVC(class_weight="balanced")}
    rows, reports, predictions = [], {}, {}
    for name, clf in candidates.items():
        model = Pipeline([("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1,2),
                         strip_accents="unicode", sublinear_tf=True)), ("classifier", clf)])
        pred = cross_val_predict(model, X, y, cv=cv)
        p, r, f, _ = precision_recall_fscore_support(y, pred, average="weighted", zero_division=0)
        rows.append({"model": name, "accuracy": accuracy_score(y,pred), "precision_weighted":p,
                     "recall_weighted":r, "f1_weighted":f})
        reports[name] = classification_report(y, pred, zero_division=0, output_dict=True)
        predictions[name] = pred
    result = pd.DataFrame(rows).sort_values("f1_weighted", ascending=False)
    best_name = result.iloc[0].model
    best = Pipeline([("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1,2),
                      strip_accents="unicode", sublinear_tf=True)), ("classifier", candidates[best_name])])
    best.fit(X,y)
    (ROOT/"models").mkdir(exist_ok=True)
    joblib.dump(best, ROOT/"models"/"intent_model.joblib")
    (ROOT/"models"/"intent_classes.json").write_text(json.dumps(sorted(y.unique().tolist()), indent=2))
    (ROOT/"reports"/"model_metrics.json").write_text(json.dumps({"validation":"3-fold stratified cross-validation",
        "seed":42,"n_examples":len(df),"warning":"Small illustrative, hand-authored corpus; scores are not evidence of clinical or broad real-world performance.",
        "best_model":best_name,"metrics":rows,"classification_reports":reports},indent=2))
    result.to_csv(ROOT/"reports"/"model_comparison.csv", index=False)
    fig, ax = plt.subplots(figsize=(9,5)); result.set_index("model")[["accuracy","precision_weighted","recall_weighted","f1_weighted"]].plot.bar(ax=ax)
    ax.set_ylim(0,1); ax.set_ylabel("Cross-validated score"); ax.set_title("Intent model comparison (small starter corpus)"); plt.xticks(rotation=15,ha="right"); fig.tight_layout()
    fig.savefig(ROOT/"reports"/"figures"/"model_comparison.png",dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7,6)); ConfusionMatrixDisplay.from_predictions(y,predictions[best_name],xticks_rotation=40,ax=ax,cmap="Blues")
    ax.set_title(f"3-fold CV confusion matrix: {best_name}"); fig.tight_layout(); fig.savefig(ROOT/"reports"/"figures"/"confusion_matrix.png",dpi=160); plt.close(fig)
    print(result.to_string(index=False)); print(f"Saved cross-validation reports; selected {best_name} for final fit.")
if __name__ == "__main__": main()
