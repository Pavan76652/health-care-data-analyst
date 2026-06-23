import { useState } from 'react';
import { api } from '../api/client';

const initial = {
  age: 65,
  gender: 'Female',
  diagnosis: 'Circulatory_390_459',
  time_in_hospital: 5,
  number_of_medications: 16,
  number_of_procedures: 1,
  number_outpatient: 0,
  number_emergency: 1,
  number_inpatient: 2,
  on_insulin: true,
  diabetes_med: true,
};

export default function PredictionTool() {
  const [form, setForm] = useState(initial);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({
      ...f,
      [name]: type === 'checkbox' ? checked : type === 'number' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.predict(form);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const riskClass =
    result?.risk_level === 'High'
      ? 'risk-badge-high'
      : result?.risk_level === 'Moderate'
        ? 'risk-badge-moderate'
        : 'risk-badge-low';

  return (
    <>
      <div className="page-header">
        <h1>Readmission Prediction Tool</h1>
        <p>Estimate 30-day readmission risk for discharge planning</p>
      </div>

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="row g-3">
                  <div className="col-md-6">
                    <label className="form-label">Age</label>
                    <input type="number" name="age" className="form-control" value={form.age} onChange={handleChange} min={0} max={110} required />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Gender</label>
                    <select name="gender" className="form-select" value={form.gender} onChange={handleChange}>
                      <option>Female</option>
                      <option>Male</option>
                    </select>
                  </div>
                  <div className="col-12">
                    <label className="form-label">Primary Diagnosis</label>
                    <select name="diagnosis" className="form-select" value={form.diagnosis} onChange={handleChange}>
                      <option value="Circulatory_390_459">Circulatory (390-459)</option>
                      <option value="Diabetes_250">Diabetes (250)</option>
                      <option value="Respiratory_460_519">Respiratory (460-519)</option>
                      <option value="Digestive_520_579">Digestive (520-579)</option>
                      <option value="Supplementary_V">Supplementary V</option>
                    </select>
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Days in Hospital</label>
                    <input type="number" name="time_in_hospital" className="form-control" value={form.time_in_hospital} onChange={handleChange} min={1} max={14} required />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Medications</label>
                    <input type="number" name="number_of_medications" className="form-control" value={form.number_of_medications} onChange={handleChange} min={0} required />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Procedures</label>
                    <input type="number" name="number_of_procedures" className="form-control" value={form.number_of_procedures} onChange={handleChange} min={0} required />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Prior Outpatient</label>
                    <input type="number" name="number_outpatient" className="form-control" value={form.number_outpatient} onChange={handleChange} min={0} />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Prior ER Visits</label>
                    <input type="number" name="number_emergency" className="form-control" value={form.number_emergency} onChange={handleChange} min={0} />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Prior Inpatient</label>
                    <input type="number" name="number_inpatient" className="form-control" value={form.number_inpatient} onChange={handleChange} min={0} />
                  </div>
                  <div className="col-12">
                    <div className="form-check">
                      <input type="checkbox" name="on_insulin" className="form-check-input" id="insulin" checked={form.on_insulin} onChange={handleChange} />
                      <label className="form-check-label" htmlFor="insulin">On insulin</label>
                    </div>
                    <div className="form-check">
                      <input type="checkbox" name="diabetes_med" className="form-check-input" id="dm" checked={form.diabetes_med} onChange={handleChange} />
                      <label className="form-check-label" htmlFor="dm">On diabetes medication</label>
                    </div>
                  </div>
                </div>
                {error && <div className="alert alert-danger mt-3 py-2">{error}</div>}
                <button type="submit" className="btn btn-primary mt-3" disabled={loading}>
                  {loading ? 'Predicting...' : 'Calculate Risk Score'}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          {result ? (
            <div className="card border-0 shadow-sm">
              <div className="card-body text-center">
                <h5 className="text-muted mb-3">Readmission Risk Score</h5>
                <div className="display-3 fw-bold text-primary mb-2">{result.risk_score}</div>
                <span className={`badge rounded-pill px-3 py-2 ${riskClass}`}>{result.risk_level} Risk</span>
                <p className="mt-3 mb-1">
                  Probability: <strong>{(result.readmission_probability * 100).toFixed(1)}%</strong>
                </p>
                <hr />
                <h6>Recommendation</h6>
                <p className="text-start small">{result.recommendation}</p>
                <h6 className="mt-3">Top Risk Factors</h6>
                <ul className="text-start small mb-0">
                  {result.top_risk_factors.map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="card border-0 shadow-sm bg-light">
              <div className="card-body text-center text-muted py-5">
                Submit patient details to generate a risk score (0–100)
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
