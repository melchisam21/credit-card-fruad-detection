# API Examples

## cURL

### POST /predict — Legitimate transaction
```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "V1": -1.3598071336738,
    "V2": -0.0727811733098497,
    "V3": 2.53634673796914,
    "V4": 1.37815522427443,
    "V5": -0.338320769942518,
    "V6": 0.462387777762292,
    "V7": 0.239598554061257,
    "V8": 0.0986979012610507,
    "V9": 0.363786969611213,
    "V10": 0.0907941719789316,
    "V11": -0.551599533260813,
    "V12": -0.617800855762348,
    "V13": -0.991389847235408,
    "V14": -0.311169353699879,
    "V15": 1.46817697209427,
    "V16": -0.470400525259478,
    "V17": 0.207971241929242,
    "V18": 0.0257905801985591,
    "V19": 0.403992960255733,
    "V20": 0.251412098239705,
    "V21": -0.018306777944153,
    "V22": 0.277837575558899,
    "V23": -0.110473910188767,
    "V24": 0.0669280749146731,
    "V25": 0.128539358273528,
    "V26": -0.189114843888824,
    "V27": 0.133558376740387,
    "V28": -0.0210530534538215,
    "scaled_amount": 149.62
  }'
```

### Expected response
```json
{
  "fraud": false,
  "probability": 0.021345,
  "threshold_used": 0.7
}
```

---

### POST /predict — Fraudulent transaction (high-risk values)
```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "V1": -3.0435406239976,
    "V2": -3.15730712090496,
    "V3": 1.08846278958118,
    "V4": 2.28864087860979,
    "V5": 1.35978818540224,
    "V6": -1.06423598602252,
    "V7": 0.325574266158614,
    "V8": -0.0677936531906252,
    "V9": -0.270952836226548,
    "V10": -1.83316635070447,
    "V11": 1.43327744470476,
    "V12": -2.45832890656951,
    "V13": -2.85914079980498,
    "V14": -3.24924747768707,
    "V15": 0.0720328899824641,
    "V16": -0.508777645715832,
    "V17": -0.99422929955993,
    "V18": -0.311169353699879,
    "V19": 0.0,
    "V20": 0.0,
    "V21": 0.0,
    "V22": 0.0,
    "V23": 0.0,
    "V24": 0.0,
    "V25": 0.0,
    "V26": 0.0,
    "V27": 0.0,
    "V28": 0.0,
    "scaled_amount": 1.0
  }'
```

### Expected response
```json
{
  "fraud": true,
  "probability": 0.894321,
  "threshold_used": 0.7
}
```

---

### GET /health
```bash
curl http://localhost:8000/health
```

### Expected response
```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true,
  "version": "1.0.0"
}
```

---

### GET /metrics
```bash
curl http://localhost:8000/metrics
```

### Expected response
```json
{
  "total_predictions": 42,
  "total_fraud_flagged": 3,
  "fraud_rate_percent": 7.1429
}
```

---

## Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
resp = requests.get(f"{BASE_URL}/health")
print(resp.json())

# Predict
transaction = {
    "V1": -1.3598071336738,
    "V2": -0.0727811733098497,
    "V3": 2.53634673796914,
    "V4": 1.37815522427443,
    "V5": -0.338320769942518,
    "V6": 0.462387777762292,
    "V7": 0.239598554061257,
    "V8": 0.0986979012610507,
    "V9": 0.363786969611213,
    "V10": 0.0907941719789316,
    "V11": -0.551599533260813,
    "V12": -0.617800855762348,
    "V13": -0.991389847235408,
    "V14": -0.311169353699879,
    "V15": 1.46817697209427,
    "V16": -0.470400525259478,
    "V17": 0.207971241929242,
    "V18": 0.0257905801985591,
    "V19": 0.403992960255733,
    "V20": 0.251412098239705,
    "V21": -0.018306777944153,
    "V22": 0.277837575558899,
    "V23": -0.110473910188767,
    "V24": 0.0669280749146731,
    "V25": 0.128539358273528,
    "V26": -0.189114843888824,
    "V27": 0.133558376740387,
    "V28": -0.0210530534538215,
    "scaled_amount": 149.62,
}

resp = requests.post(f"{BASE_URL}/predict", json=transaction)
result = resp.json()

print(f"Fraud: {result['fraud']}")
print(f"Probability: {result['probability']:.4f}")
print(f"Threshold: {result['threshold_used']}")
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": { "name": "Fraud Detection API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "item": [
    {
      "name": "Health Check",
      "request": { "method": "GET", "url": "http://localhost:8000/health" }
    },
    {
      "name": "Predict - Legit",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\"V1\":-1.3598071336738,\"V2\":-0.0727811733098,\"V3\":2.5363467379,\"V4\":1.3781552242,\"V5\":-0.3383207699,\"V6\":0.4623877777,\"V7\":0.2395985540,\"V8\":0.0986979012,\"V9\":0.3637869696,\"V10\":0.0907941719,\"V11\":-0.5515995332,\"V12\":-0.6178008557,\"V13\":-0.9913898472,\"V14\":-0.3111693536,\"V15\":1.4681769720,\"V16\":-0.4704005252,\"V17\":0.2079712419,\"V18\":0.0257905801,\"V19\":0.4039929602,\"V20\":0.2514120982,\"V21\":-0.0183067779,\"V22\":0.2778375755,\"V23\":-0.1104739101,\"V24\":0.0669280749,\"V25\":0.1285393582,\"V26\":-0.1891148438,\"V27\":0.1335583767,\"V28\":-0.0210530534,\"scaled_amount\":149.62}"
        },
        "url": "http://localhost:8000/predict"
      }
    },
    {
      "name": "Metrics",
      "request": { "method": "GET", "url": "http://localhost:8000/metrics" }
    }
  ]
}
```
