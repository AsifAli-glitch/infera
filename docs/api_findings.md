# FortyGuard API — Findings Log

Update this as each "TO VERIFY" item gets resolved. Paste raw JSON snippets
where useful. This is the single source of truth the whole team should check
before writing pipeline code against assumed field names.

## Confirmed
- Base URL: `https://api.fortyguard.com/v1/`
- Auth: header `api-key: YOUR_KEY`
- Async pattern: POST submits job -> `activity_id` -> GET `/v1/status/{activity_id}` to poll

## Still to verify (update status + notes as you test)

| Item | Status | Notes |
|---|---|---|
| Full field schema of Create Heatmap response (grid, cells, lat/lon per cell) | ⬜ open | |
| Units — Celsius or Fahrenheit | ⬜ open | |
| What Heat Intelligence returns | ⬜ open | |
| What Environmental Parameters returns | ⬜ open | |
| Rate limits / credit cost per call | ⬜ open | |
| Historical data depth (days/weeks/months) | ⬜ open | |
| Error response shape for invalid/partial-coverage AOI | ⬜ open | |
| Exact endpoint path slugs (confirm against real docs) | ⬜ open | client currently guesses `create-heatmap`, `heat-intelligence`, etc. |

## Raw response samples
Paste real JSON here as you get it, labeled by endpoint and AOI used.
