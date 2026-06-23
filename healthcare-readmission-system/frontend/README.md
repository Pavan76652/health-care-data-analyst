# React Frontend — Healthcare Readmission Analytics

Hospital administrator dashboard connected to the FastAPI backend.

## Pages

| Page | Route | Features |
|------|-------|----------|
| Login | `/login` | Demo auth |
| Dashboard | `/dashboard` | KPIs + Chart.js visuals |
| Patient Analytics | `/patients` | Search, filters, pagination, CSV export |
| Prediction Tool | `/predict` | ML risk score 0–100 |
| Reports | `/reports` | Analytics + CSV/PDF export |

## Demo Login

- Email: `admin@hospital.com`
- Password: `admin123`

## Run (development)

Terminal 1 — API:
```bash
python backend/scripts/run_api.py
```

Terminal 2 — Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

Vite proxies `/api` → `http://localhost:8000`

## Build for production

```bash
npm run build
npm run preview
```

## Stack

- React 18 + Vite
- React Router
- Bootstrap 5
- Chart.js + react-chartjs-2
- jsPDF (PDF export)
