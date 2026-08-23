"""
fortyguard_client.py

Minimal, reusable client for the FortyGuard API's async submit -> poll pattern.
Covers: Create Heatmap, Heat Intelligence, Environmental Parameters,
Satellite View Segmentation, Street View Segmentation, Check Status,
Check API Credits Usage.

Usage:
    from fortyguard_client import FortyGuardClient

    client = FortyGuardClient()  # reads FORTYGUARD_API_KEY from env
    job = client.create_heatmap(polygon_aoi, start_date="2026-08-20",
                                 start_time="12:00", filter_type="snapshot",
                                 granularity="high")
    result = client.poll_until_complete(job["activity_id"])
    print(result)

Set your key as an environment variable before running, e.g.:
    export FORTYGUARD_API_KEY="your_key_here"
Never hardcode the key in this file or commit it to git.
"""

import os
import time
import json
from pathlib import Path
from typing import Optional

import requests

BASE_URL = "https://api.fortyguard.com/v1"
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"


class FortyGuardAPIError(Exception):
    pass


class FortyGuardClient:
    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True):
        self.api_key = api_key or os.environ.get("FORTYGUARD_API_KEY")
        if not self.api_key:
            raise FortyGuardAPIError(
                "No API key found. Set FORTYGUARD_API_KEY as an environment "
                "variable or pass api_key= explicitly."
            )
        self.headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        self.use_cache = use_cache
        if self.use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # ---------- low-level helpers ----------

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{BASE_URL}/{endpoint}"
        resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
        if not resp.ok:
            raise FortyGuardAPIError(f"POST {endpoint} failed [{resp.status_code}]: {resp.text}")
        return resp.json()

    def _get(self, endpoint: str) -> dict:
        url = f"{BASE_URL}/{endpoint}"
        resp = requests.get(url, headers=self.headers, timeout=30)
        if not resp.ok:
            raise FortyGuardAPIError(f"GET {endpoint} failed [{resp.status_code}]: {resp.text}")
        return resp.json()

    # ---------- submit-job endpoints (all async: submit -> activity_id) ----------

    def create_heatmap(self, polygon_aoi: dict, start_date: str, start_time: str,
                        filter_type: str, granularity: str) -> dict:
        payload = {
            "polygon_aoi": polygon_aoi,
            "date_time": {
                "start_date": start_date,
                "start_time": start_time,
                "filter_type": filter_type,
            },
            "granularity": granularity,
        }
        return self._post("create-heatmap", payload)

    def heat_intelligence(self, polygon_aoi: dict, **kwargs) -> dict:
        payload = {"polygon_aoi": polygon_aoi, **kwargs}
        return self._post("heat-intelligence", payload)

    def environmental_parameters(self, polygon_aoi: dict, **kwargs) -> dict:
        payload = {"polygon_aoi": polygon_aoi, **kwargs}
        return self._post("environmental-parameters", payload)

    def satellite_view_segmentation(self, polygon_aoi: dict, **kwargs) -> dict:
        payload = {"polygon_aoi": polygon_aoi, **kwargs}
        return self._post("satellite-view-segmentation", payload)

    def street_view_segmentation(self, polygon_aoi: dict, **kwargs) -> dict:
        payload = {"polygon_aoi": polygon_aoi, **kwargs}
        return self._post("street-view-segmentation", payload)

    # NOTE: endpoint path strings above (e.g. "create-heatmap") are best-guess
    # slugs based on the blueprint's naming — confirm exact paths against the
    # real API docs and fix here if they differ. This is your day-1 task.

    # ---------- status / credits ----------

    def check_status(self, activity_id: str) -> dict:
        return self._get(f"status/{activity_id}")

    def check_credits_usage(self) -> dict:
        return self._get("credits-usage")

    # ---------- polling wrapper ----------

    def poll_until_complete(self, activity_id: str, interval_s: float = 3.0,
                             timeout_s: float = 180.0, cache_key: Optional[str] = None) -> dict:
        """Poll Check Status until the job finishes, fails, or times out.
        Caches the final result locally (if use_cache) so repeated dev runs
        don't burn API credits re-fetching the same AOI."""
        cache_path = None
        if self.use_cache and cache_key:
            cache_path = CACHE_DIR / f"{cache_key}.json"
            if cache_path.exists():
                return json.loads(cache_path.read_text())

        start = time.time()
        while time.time() - start < timeout_s:
            status = self.check_status(activity_id)
            state = status.get("status") or status.get("state")
            if state in ("complete", "completed", "success", "done"):
                if cache_path:
                    cache_path.write_text(json.dumps(status, indent=2))
                return status
            if state in ("failed", "error"):
                raise FortyGuardAPIError(f"Job {activity_id} failed: {status}")
            time.sleep(interval_s)
        raise FortyGuardAPIError(f"Job {activity_id} timed out after {timeout_s}s")


if __name__ == "__main__":
    # Quick manual smoke test — run: python fortyguard_client.py
    # Replace with a real neighborhood polygon before running.
    example_aoi = {
        "type": "Polygon",
        "coordinates": [[
            [55.2708, 25.2048],
            [55.2808, 25.2048],
            [55.2808, 25.2148],
            [55.2708, 25.2148],
            [55.2708, 25.2048],
        ]],
    }

    client = FortyGuardClient()
    job = client.create_heatmap(
        polygon_aoi=example_aoi,
        start_date="2026-08-20",
        start_time="12:00",
        filter_type="snapshot",
        granularity="high",
    )
    print("Submitted job:", job)

    result = client.poll_until_complete(job["activity_id"], cache_key="test_aoi_1")
    print(json.dumps(result, indent=2)[:2000])
