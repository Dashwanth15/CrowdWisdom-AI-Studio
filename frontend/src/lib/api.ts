import axios, { AxiosInstance, AxiosResponse } from 'axios'

export const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '')

const apiClient: AxiosInstance = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 65000,
})

// Request interceptor — attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — redirect on 401
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: any) => apiClient.post('/auth/register', data),
  me: () => apiClient.get('/auth/me'),
}

// Dashboard
export const dashboardApi = {
  stats: () => apiClient.get('/dashboard/stats'),
}

// Campaigns
export const campaignsApi = {
  list: (params?: any) => apiClient.get('/campaigns', { params }),
  get: (id: string) => apiClient.get(`/campaigns/${id}`),
  create: (data: any) => apiClient.post('/campaigns', data),
  update: (id: string, data: any) => apiClient.patch(`/campaigns/${id}`, data),
  delete: (id: string) => apiClient.delete(`/campaigns/${id}`),
  duplicate: (id: string) => apiClient.post(`/campaigns/${id}/duplicate`),
  repairLocalization: (id: string) => apiClient.post(`/campaigns/${id}/repair-localization`),
}

// Agents
export const agentsApi = {
  launchResearch: (data: any) => apiClient.post('/agents/research/launch', data),
  generateScript: (data: any) => apiClient.post('/agents/scripts/generate', data),
  cancelExecution: (id: string) => apiClient.post(`/agents/${id}/cancel`),
  retryExecution: (id: string) => apiClient.post(`/agents/${id}/retry`),
  listExecutions: (params?: any) => apiClient.get('/agents/executions', { params }),
  getExecution: (id: string) => apiClient.get(`/agents/executions/${id}`),
  getExecutionLogs: (id: string) => apiClient.get(`/agents/executions/${id}/logs`),
}

// Scripts
export const scriptsApi = {
  list: (params?: any) => apiClient.get('/scripts', { params }),
  get: (id: string) => apiClient.get(`/scripts/${id}`),
  approve: (id: string) => apiClient.post(`/scripts/${id}/approve`),
  reject: (id: string, reason: string) => apiClient.post(`/scripts/${id}/reject`, { reason }),
  update: (id: string, data: any) => apiClient.patch(`/scripts/${id}`, data),
  delete: (id: string) => apiClient.delete(`/scripts/${id}`),
  clearFailed: () => apiClient.delete('/scripts/clear-failed'),
  localize: (id: string, country?: string) => apiClient.post(`/scripts/${id}/localize`, { country }),
  getExportUrl: (id: string) => `${apiBaseUrl}/scripts/${id}/export`,
}

// Videos
export const videosApi = {
  generate: (data: any) => apiClient.post('/videos/generate', data),
  list: (params?: any) => apiClient.get('/videos', { params }),
  get: (id: string) => apiClient.get(`/videos/${id}`),
  retry: (id: string) => apiClient.post(`/videos/${id}/retry`),
  delete: (id: string) => apiClient.delete(`/videos/${id}`),
  clearFailed: () => apiClient.delete('/videos/clear-failed'),
}

// Research
export const researchApi = {
  listJobs: (params?: any) => apiClient.get('/research/jobs', { params }),
  getJob: (id: string) => apiClient.get(`/research/jobs/${id}`),
  listAds: (params?: any) => apiClient.get('/research/advertisements', { params }),
  getAd: (id: string) => apiClient.get(`/research/advertisements/${id}`),
  listInsights: (params?: any) => apiClient.get('/research/insights', { params }),
  associateCampaign: (data: { campaign_id: string; ad_ids: string[] }) =>
    apiClient.post('/research/associate-campaign', data),
  getExportUrl: (campaign_id?: string) =>
    campaign_id ? `${apiBaseUrl}/research/advertisements/export?campaign_id=${campaign_id}` : `${apiBaseUrl}/research/advertisements/export`,
}

// Creative Briefs (Checkpoint 1)
export const creativeBriefsApi = {
  generate: (campaign_id: string, custom_instructions?: string) =>
    apiClient.post('/creative-briefs/generate', { campaign_id, custom_instructions }),
  list: (params?: any) => apiClient.get('/creative-briefs', { params }),
  get: (id: string) => apiClient.get(`/creative-briefs/${id}`),
  getByCampaign: (campaign_id: string) => apiClient.get(`/creative-briefs/campaign/${campaign_id}`),
  approve: (id: string) => apiClient.post(`/creative-briefs/${id}/approve`),
  reject: (id: string, reason: string) => apiClient.post(`/creative-briefs/${id}/reject`, { reason }),
}

// Integrations
export const integrationsApi = {
  list: () => apiClient.get('/integrations'),
  update: (provider: string, data: any) => apiClient.patch(`/integrations/${provider}`, data),
  test: (provider: string) => apiClient.post(`/integrations/${provider}/test`),
}

// Assets
export const assetsApi = {
  list: (params?: any) => apiClient.get('/assets', { params }),
  delete: (id: string) => apiClient.delete(`/assets/${id}`),
}

// Workflows
export const workflowApi = {
  listTasks: (params?: any) => apiClient.get('/workflows/tasks', { params }),
}

// Market Intelligence (India 🇮🇳 & Philippines 🇵🇭)
export const marketIntelligenceApi = {
  getCountries: () => apiClient.get('/market-intelligence/countries'),
  getOverview: (country: string) => apiClient.get(`/market-intelligence/${country}/overview`),
  getAudiences: (country: string, params?: any) => apiClient.get(`/market-intelligence/${country}/audiences`, { params }),
  getTrends: (country: string, params?: any) => apiClient.get(`/market-intelligence/${country}/trends`, { params }),
  research: (data: { country: string; query: string; category?: string; max_results?: number }) =>
    apiClient.post('/market-intelligence/research', data),
  getRecommendations: (country: string) => apiClient.get(`/market-intelligence/${country}/recommendations`),
  getCampaignContext: (campaignId: string) => apiClient.get(`/market-intelligence/campaign/${campaignId}`),
  validateCompliance: (data: { country_code: string; text_content: string; content_type?: string }) =>
    apiClient.post('/market-intelligence/validate-compliance', data),
  getProviderHealth: () => apiClient.get('/market-intelligence/provider-health'),
  getComparison: () => apiClient.get('/market-intelligence/comparison'),
  getCompetitorAds: (params?: any) => apiClient.get('/market-intelligence/competitor-ads', { params }),
}

export const api = {
  get: apiClient.get,
  post: apiClient.post,
  patch: apiClient.patch,
  put: apiClient.put,
  delete: apiClient.delete,
}

export default apiClient
