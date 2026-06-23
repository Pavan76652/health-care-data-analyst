const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => request('/health'),
  getPatients: (page = 1, pageSize = 25, search = '') => {
    const params = new URLSearchParams({ page, page_size: pageSize });
    if (search) params.set('search', search);
    return request(`/patients?${params}`);
  },
  getAnalytics: () => request('/analytics'),
  getDashboard: () => request('/dashboard'),
  predict: (payload) =>
    request('/predict', { method: 'POST', body: JSON.stringify(payload) }),
};
