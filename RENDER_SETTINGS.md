# Render settings (PRISM Brain Backend v3.0.0 - Live Probabilities)

Use these exact values in Render **Web Service** settings:

- **Root Directory**: *(empty)*
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn full_calculator_live:app --host 0.0.0.0 --port $PORT`

After saving, run **Manual Deploy → Clear build cache & deploy**.

## Verify
- Health: `/api/health` → `calculator_version: "3.0.0"`
- Docs: `/docs`
- Trigger update (manual): `POST /api/probabilities/update`
