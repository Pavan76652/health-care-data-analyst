export default function KpiCard({ label, value, suffix = '' }) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">
        {value}
        {suffix && <span className="fs-6 text-muted">{suffix}</span>}
      </div>
    </div>
  );
}
