const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export interface DashboardStats {
  total_regulations: number;
  high_impact_regulations: number;
  total_alerts: number;
  alerts_sent: number;
  active_subscribers: number;
}

export interface Regulation {
  id: number;
  title: string;
  document_number: string | null;
  abstract: string | null;
  summary: string | null;
  impact_level: string | null;
  publication_date: string | null;
  effective_date: string | null;
  source_url: string | null;
  industry: string | null;
  created_at: string | null;
}

export interface Alert {
  id: number;
  subscriber: { id: number; name: string; email: string };
  regulation: { id: number; title: string; impact_level: string };
  delivery_status: string;
  is_read: boolean;
  sent_at: string | null;
  created_at: string | null;
}

export interface Subscriber {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  industries: string[];
  created_at: string | null;
}

export const api = {
  getDashboardStats: () => request<DashboardStats>('/dashboard/stats'),

  getRegulations: (params?: { industry?: string; impact_level?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.industry) searchParams.set('industry', params.industry);
    if (params?.impact_level) searchParams.set('impact_level', params.impact_level);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    const qs = searchParams.toString();
    return request<{ total: number; regulations: Regulation[] }>(`/regulations${qs ? '?' + qs : ''}`);
  },

  getRegulation: (id: number) => request<Regulation>(`/regulations/${id}`),

  getAlerts: (params?: { status?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set('status', params.status);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    const qs = searchParams.toString();
    return request<{ total: number; alerts: Alert[] }>(`/alerts${qs ? '?' + qs : ''}`);
  },

  getAlertStats: () => request<{ total: number; sent: number; pending: number; failed: number }>('/alerts/stats'),

  getSubscribers: () => request<{ subscribers: Subscriber[] }>('/subscriptions'),

  createSubscriber: (data: { email: string; name: string; industries: string[] }) =>
    request<Subscriber>('/subscriptions', { method: 'POST', body: JSON.stringify(data) }),

  deleteSubscriber: (id: number) =>
    request<{ status: string }>(`/subscriptions/${id}`, { method: 'DELETE' }),

  triggerMonitoring: () => request<{ status: string; message: string }>('/monitor/trigger', { method: 'POST' }),

  getIndustries: () => request<{ industries: { id: number; name: string; slug: string; description: string }[] }>('/sources/industries'),
};
