services:
  - type: web
    name: fraud-detection-api
    runtime: docker
    plan: free
    dockerfilePath: Dockerfile
    dockerContext: .
    healthCheckPath: /health
    envVars:
      - key: PORT
        value: "8000"
      - key: FRAUD_THRESHOLD
        value: "0.7"
      - key: DEBUG
        value: "false"
      - key: LOG_DB_PATH
        value: "./logs/predictions.db"
