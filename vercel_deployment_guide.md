# 🚀 Frontend Deployment Guide — Vercel

This guide covers deploying your clean, single-page frontend (HTML/CSS/JS) to [Vercel](https://vercel.com/) for fast, global edge hosting.

---

## 1. Directory Structure Check
Ensure your frontend files are neatly contained in the `frontend/` directory of your project:

```
credit-card-fraud-detection/
└── frontend/
    ├── index.html
    ├── style.css
    ├── script.js
    └── vercel.json
```

The included `vercel.json` ensures that Vercel serves the correct security headers and routes requests to `index.html`.

---

## 2. Connect Your Backend (Important)

Before deploying to Vercel, make sure you know your **production backend URL** (from Render, e.g., `https://fraud-detection-api.onrender.com`).

1. Open `frontend/script.js`.
2. Locate the `API_URL` configuration block at the top.
3. Update it to point to your live Render API URL:

```javascript
// ── Configuration ────────────────────────────────────────────────
const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : "https://fraud-detection-api.onrender.com"; // <-- Update this!
```

---

## 3. Deploy via Vercel Dashboard

1. **Push your code to GitHub** (make sure the `frontend` folder is committed).
2. Log in to [Vercel](https://vercel.com).
3. Click **Add New...** and select **Project**.
4. Import your GitHub repository (`credit-card-fraud-detection`).
5. **Crucial Configuration Step**:
   - In the "Framework Preset" dropdown, select **Other**.
   - Note: Since we have the backend and frontend in the same repo, we need to tell Vercel to only build the frontend.
   - Set the **Root Directory** to `frontend`.
6. Click **Deploy**.

Vercel will quickly build and deploy the HTML/JS application and provide you with a live URL (e.g., `https://fraud-shield-ui.vercel.app`).

---

## 4. Test the Integration

1. Go to your new Vercel URL.
2. Check the top right **Health Badge**. If everything is correct, it will say **API Online** in green.
3. Click **Quick Test > Suspicious Sample**.
4. Click **Analyze Transaction**.
5. Ensure the gauge animations load and the result displays correctly.

---

## 5. Troubleshooting CORS

If the Health badge shows offline, but the Render API works in your terminal:
Open your browser's Developer Tools (F12) -> Console. If you see a **CORS error**, verify that in your FastAPI `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, change to ["https://fraud-shield-ui.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Currently, `allow_origins=["*"]` is set, so it should work out of the box. Once everything works, you can lock it down to your specific Vercel URL for better security.
