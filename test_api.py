"""
test_api.py — Quick smoke-tests for the fraud detection API.
Run with:  python test_api.py
"""

import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000"

LEGIT_TX = {
    "V1": -1.3598071336738, "V2": -0.0727811733098, "V3": 2.53634673796914,
    "V4": 1.37815522427443, "V5": -0.33832077, "V6": 0.46238778, "V7": 0.23959855,
    "V8": 0.09869790, "V9": 0.36378697, "V10": 0.09079417, "V11": -0.55159953,
    "V12": -0.61780086, "V13": -0.99138985, "V14": -0.31116935, "V15": 1.46817697,
    "V16": -0.47040053, "V17": 0.20797124, "V18": 0.02579058, "V19": 0.40399296,
    "V20": 0.25141210, "V21": -0.01830678, "V22": 0.27783758, "V23": -0.11047391,
    "V24": 0.06692807, "V25": 0.12853936, "V26": -0.18911484, "V27": 0.13355838,
    "V28": -0.02105305, "scaled_amount": 149.62,
}


def get(path):
    with urllib.request.urlopen(BASE + path) as r:
        return r.status, json.loads(r.read())


def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE + path, data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print("=" * 55)


# ── 1. Health ────────────────────────────────────────────────
section("GET /health")
status, body = get("/health")
print(json.dumps(body, indent=2))
assert status == 200
assert body["status"] == "healthy"
assert body["model_loaded"] is True
assert body["scaler_loaded"] is True
print("✓  PASSED")

# ── 2. Predict — legitimate transaction ──────────────────────
section("POST /predict  (legitimate transaction)")
status, body = post("/predict", LEGIT_TX)
print(json.dumps(body, indent=2))
assert status == 200
assert "fraud" in body
assert "probability" in body
assert 0.0 <= body["probability"] <= 1.0
print(f"✓  PASSED  |  fraud={body['fraud']}  prob={body['probability']:.6f}")

# ── 3. Metrics ───────────────────────────────────────────────
section("GET /metrics")
status, body = get("/metrics")
print(json.dumps(body, indent=2))
assert status == 200
assert body["total_predictions"] >= 1      # at least the one we just made
print("✓  PASSED")

# ── 4. Validation — missing fields ───────────────────────────
section("POST /predict  (missing fields) → expect HTTP 422")
status, body = post("/predict", {"V1": 1.0, "V2": 0.5})
print("HTTP status:", status)
print("Errors count:", len(body.get("detail", [])))
assert status == 422
print("✓  PASSED")

# ── 5. Validation — unknown extra field ──────────────────────
section("POST /predict  (unknown field) → expect HTTP 422")
bad_tx = dict(LEGIT_TX)
bad_tx["HACKER_FIELD"] = 999
status, body = post("/predict", bad_tx)
msg = body.get("detail", [{}])[0].get("msg", "")
print("HTTP status:", status)
print("Error msg:", msg)
assert status == 422
print("✓  PASSED")

print("\n" + "=" * 55)
print("  ALL TESTS PASSED")
print("=" * 55 + "\n")
