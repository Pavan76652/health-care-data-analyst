import { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { api } from '../api/client';
import { exportToCsv } from '../utils/exportCsv';
import { exportReportPdf } from '../utils/exportPdf';
import KpiCard from '../components/KpiCard';

export default function Reports() {
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getAnalytics()
      .then(setAnalytics)
      .catch((e) => setError(e.message));
  }, []);

  const handleCsv = () => {
    if (!analytics) return;
    const rows = analytics.top_diagnoses.map((d) => ({
      diagnosis: d.diag_1_group,
      admissions: d.admissions,
      readmission_rate_pct: d.readmission_rate,
    }));
    exportToCsv('readmission_report.csv', rows);
  };

  const handlePdf = () => {
    if (!analytics) return;
    const k = analytics.kpis;
    exportReportPdf({
      title: 'Healthcare Readmission Analytics Report',
      kpis: [
        { label: 'Total Patients', value: k.total_patients.toLocaleString() },
        { label: 'Readmission Rate (30-day)', value: `${k.readmission_rate_30_day_pct}%` },
        { label: 'Average LOS', value: `${k.average_length_of_stay} days` },
        { label: 'High Risk Patients', value: k.high_risk_patients.toLocaleString() },
      ],
      tableHeaders: ['Diagnosis', 'Admissions', 'Readmit %'],
      tableRows: analytics.top_diagnoses.slice(0, 10).map((d) => [
        d.diag_1_group,
        String(d.admissions),
        String(d.readmission_rate),
      ]),
      filename: 'readmission_executive_report.pdf',
    });
  };

  if (error) {
    return <div className="alert alert-warning">{error}</div>;
  }

  if (!analytics) {
    return <div className="text-center py-5">Loading report data...</div>;
  }

  const k = analytics.kpis;
  const diagChart = {
    labels: analytics.top_diagnoses.map((d) => d.diag_1_group),
    datasets: [
      {
        label: 'Readmission Rate %',
        data: analytics.top_diagnoses.map((d) => d.readmission_rate),
        backgroundColor: '#e74c3c',
      },
    ],
  };

  return (
    <>
      <div className="page-header d-flex flex-wrap justify-content-between align-items-start gap-2">
        <div>
          <h1>Reports</h1>
          <p>Executive summaries and exports</p>
        </div>
        <div className="d-flex gap-2">
          <button type="button" className="btn btn-outline-primary" onClick={handleCsv}>
            Export CSV
          </button>
          <button type="button" className="btn btn-primary" onClick={handlePdf}>
            Export PDF
          </button>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <KpiCard label="Total Patients" value={k.total_patients.toLocaleString()} />
        </div>
        <div className="col-md-3">
          <KpiCard label="Readmission Rate" value={k.readmission_rate_30_day_pct} suffix="%" />
        </div>
        <div className="col-md-3">
          <KpiCard label="Avg LOS" value={k.average_length_of_stay} suffix=" days" />
        </div>
        <div className="col-md-3">
          <KpiCard label="High Risk" value={k.high_risk_patients.toLocaleString()} />
        </div>
      </div>

      <div className="row g-3">
        <div className="col-lg-8">
          <div className="chart-card" style={{ height: 360 }}>
            <h6 className="mb-3">Readmission Rate by Top Diagnoses</h6>
            <Bar data={diagChart} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>
        <div className="col-lg-4">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-header bg-white fw-semibold">Age Breakdown</div>
            <ul className="list-group list-group-flush">
              {analytics.readmission_by_age.map((row) => (
                <li key={row.age} className="list-group-item d-flex justify-content-between">
                  <span>{row.age}</span>
                  <span className="text-muted">{row.readmission_rate}%</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
