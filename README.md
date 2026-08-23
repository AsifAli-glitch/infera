# Infera — AI Urban Heat Risk Predictor

Built for **FortyGuard Hackathon '26**. Turns FortyGuard's hyperlocal
(2m-resolution, street-level) temperature data into area-level heat-risk
scores, hotspot maps, and plain-language recommendations for city planners.

## Why

Standard weather forecasts give one number for an entire city. Urban heat is
hyperlocal — two neighborhoods 500m apart can differ by several degrees.
Infera makes that variation visible, quantified, and actionable.

## How it works

```
FortyGuard API (temperature grid)
  -> cleaning + validation
  -> feature engineering (local deviation, percentile rank)
  -> hotspot detection (DBSCAN + Isolation Forest, cross-validated)
  -> rule-based risk score (0-100) + category
  -> recommendation engine
  -> interactive map (folium)
```

We deliberately use a **transparent rule-based score + unsupervised anomaly
detection**, not a supervised classifier — there's no labeled "ground truth"
risk data to train or validate one against, and we'd rather be honest about
that than fake an accuracy number.

## Setup

```bash
git clone <this-repo-url>
cd infera
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your FortyGuard API key
```

## Run

```bash
python src/fortyguard_client.py   # smoke-test the API client
jupyter notebook notebooks/       # or open in Google Colab
```

## Team

| Member | Owns |
|---|---|
| Member 1 | Data pipeline, feature engineering, DBSCAN / Isolation Forest, risk score |
| Member 2 | API integration, auth, polling, caching, error handling |
| Member 3 | Dashboard (folium/Streamlit), recommendation display, demo integration |

## Status

See `docs/api_findings.md` for what's confirmed vs. still being verified
against the live API.

## License

MIT (or update as needed for submission rules).
