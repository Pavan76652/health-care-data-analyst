import { useEffect, useState } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { api } from '../api/client';
import KpiCard from '../components/KpiCard';

const chartOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
};

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getDashboard()
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="alert alert-warning">
        Could not load dashboard. Start the API: <code>python backend/scripts/run_api.py</code>
        <br />
        {error}
      </div>
    );
  }

  if (!data) {
    return <div className="text-center py-5">Loading dashboard...</div>;
  }

  const k = data.kpis;
  const charts = data.charts;

  const ageChart = {
    labels: charts.readmission_by_age.map((r) => r.age),
    datasets: [
      {
        label: 'Readmission Rate %',
        data: charts.readmission_by_age.map((r) => r.readmission_rate_pct),
        backgroundColor: '#2e86c1',
      },
    ],
  };

  const genderChart = {
    labels: charts.readmission_by_gender.map((r) => r.gender),
    datasets: [
      {
        data: charts.readmission_by_gender.map((r) => r.admissions),
        backgroundColor: ['#9b59b6', '#3498db', '#95a5a6'],
      },
    ],
  };

  const trendChart = {
    labels: charts.monthly_trends.map((r) => r.month_name),
    datasets: [
      {
        label: 'Admissions',
        data: charts.monthly_trends.map((r) => r.admissions),
        borderColor: '#1b4f72',
        tension: 0.3,
      },
      {
        label: 'Readmit %',
        data: charts.monthly_trends.map((r) => r.readmission_rate_pct),
        borderColor: '#e74c3c',
        tension: 0.3,
        yAxisID: 'y1',
      },
    ],
  };

  const diagChart = {
    labels: charts.readmission_by_diagnosis.slice(0, 8).map((r) => r.diag_1_group),
    datasets: [
      {
        label: 'Admissions',
        data: charts.readmission_by_diagnosis.slice(0, 8).map((r) => r.admissions),
        backgroundColor: '#16a085',
      },
    ],
  };

  return (
    <>
      <div className="page-header">
        <h1>Executive Dashboard</h1>
        <p>Hospital readmission KPIs and trends</p>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-4 col-lg">
          <KpiCard label="Total Patients" value={Number(k.total_patients).toLocaleString()} />
        </div>
        <div className="col-md-4 col-lg">
          <KpiCard label="Readmission Rate" value={k.readmission_rate_pct} suffix="%" />
        </div>
        <div className="col-md-4 col-lg">
          <KpiCard label="Avg Length of Stay" value={k.avg_length_of_stay} suffix=" days" />
        </div>
        <div className="col-md-4 col-lg">
          <KpiCard label="High Risk Patients" value={Number(k.high_risk_patients).toLocaleString()} />
        </div>
        <div className="col-md-4 col-lg">
          <KpiCard label="Top Diagnosis" value={String(k.top_diagnosis).replace(/_/g, ' ')} />
        </div>
      </div>

      <div className="row g-3">
        <div className="col-lg-6">
          <div className="chart-card" style={{ height: 320 }}>
            <h6 className="mb-3">Readmission by Age</h6>
            <Bar data={ageChart} options={chartOpts} />
          </div>
        </div>
        <div className="col-lg-6">
          <div className="chart-card" style={{ height: 320 }}>
            <h6 className="mb-3">Admissions by Gender</h6>
            <Doughnut data={genderChart} options={chartOpts} />
          </div>
        </div>
        <div className="col-lg-6">
          <div className="chart-card" style={{ height: 320 }}>
            <h6 className="mb-3">Monthly Trends</h6>
            <Line
              data={trendChart}
              options={{
                ...chartOpts,
                scales: {
                  y: { position: 'left' },
                  y1: { position: 'right', grid: { drawOnChartArea: false } },
                },
              }}
            />
          </div>
        </div>
        <div className="col-lg-6">
          <div className="chart-card" style={{ height: 320 }}>
            <h6 className="mb-3">Top Diagnoses</h6>
            <Bar data={diagChart} options={{ ...chartOpts, indexAxis: 'y' }} />
          </div>
        </div>
      </div>
    </>
  );
}
