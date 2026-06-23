import { useEffect, useState, useCallback } from 'react';
import { api } from '../api/client';
import { exportToCsv } from '../utils/exportCsv';

export default function PatientAnalytics() {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    api.getPatients(page, 25, search)
      .then(setData)
      .finally(() => setLoading(false));
  }, [page, search]);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [load]);

  const items = (data?.items || []).filter((row) =>
    riskFilter === 'all' ? true : row.risk_tier === riskFilter
  );

  const handleExport = () => {
    exportToCsv('patients_export.csv', items);
  };

  const totalPages = data ? Math.ceil(data.total_records / data.page_size) : 1;

  return (
    <>
      <div className="page-header d-flex flex-wrap justify-content-between align-items-start gap-2">
        <div>
          <h1>Patient Analytics</h1>
          <p>Search and filter admission records</p>
        </div>
        <button type="button" className="btn btn-outline-primary" onClick={handleExport} disabled={!items.length}>
          Export CSV
        </button>
      </div>

      <div className="card border-0 shadow-sm mb-3">
        <div className="card-body">
          <div className="row g-2">
            <div className="col-md-6">
              <input
                type="search"
                className="form-control"
                placeholder="Search patient ID, gender, diagnosis..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              />
            </div>
            <div className="col-md-4">
              <select
                className="form-select"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
              >
                <option value="all">All risk tiers</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Moderate">Moderate</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="card border-0 shadow-sm">
        <div className="table-responsive">
          <table className="table table-hover mb-0">
            <thead className="table-light">
              <tr>
                <th>Patient ID</th>
                <th>Gender</th>
                <th>Age</th>
                <th>Diagnosis</th>
                <th>LOS</th>
                <th>Meds</th>
                <th>Readmitted</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-4">Loading...</td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-4">No records found</td></tr>
              ) : (
                items.map((row) => (
                  <tr key={row.admission_id}>
                    <td>{row.patient_id}</td>
                    <td>{row.gender}</td>
                    <td>{row.age}</td>
                    <td><small>{row.diag_1_group}</small></td>
                    <td>{row.time_in_hospital}d</td>
                    <td>{row.num_medications}</td>
                    <td>
                      <span className={`badge ${row.readmitted_flag === 'Yes' ? 'bg-danger' : 'bg-success'}`}>
                        {row.readmitted_flag}
                      </span>
                    </td>
                    <td>
                      <span className={`badge bg-${row.risk_tier === 'Critical' || row.risk_tier === 'High' ? 'danger' : row.risk_tier === 'Moderate' ? 'warning' : 'secondary'}`}>
                        {row.risk_tier}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="card-footer d-flex justify-content-between align-items-center">
          <small className="text-muted">
            {data ? `${data.total_records.toLocaleString()} total records` : ''}
          </small>
          <div className="btn-group">
            <button type="button" className="btn btn-sm btn-outline-secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </button>
            <span className="btn btn-sm btn-light disabled">Page {page} / {totalPages}</span>
            <button type="button" className="btn btn-sm btn-outline-secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Next
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
