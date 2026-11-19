"""Download a small reproducible drug-label sample from the FDA openFDA API."""
import json, pathlib, requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "openfda_drug_labels.json"
API = "https://api.fda.gov/drug/label.json"

def main():
    # The result is a live sample, not a full or complete catalogue. FDA API records
    # can include submitted copyrighted text; use only for educational analysis and
    # retain record attribution and the API terms alongside redistributed data.
    rows = []
    for term in ("ibuprofen", "metformin", "acetaminophen", "amoxicillin", "aspirin"):
        params = {"search": f'openfda.generic_name:"{term}"', "limit": 10}
        response = requests.get(API, params=params, timeout=45)
        if response.status_code == 404:
            continue
        response.raise_for_status()
        rows.extend(response.json().get("results", []))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} label records to {OUT}")

if __name__ == "__main__": main()
