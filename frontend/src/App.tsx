import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/AppLayout'
import { LoginPage } from '@/pages/auth/LoginPage'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { CampaignsPage } from '@/pages/campaigns/CampaignsPage'
import { CampaignDetailPage } from '@/pages/campaigns/CampaignDetailPage'
import { AgentCommandCenterPage } from '@/pages/agents/AgentCommandCenterPage'
import { ResearchPage } from '@/pages/research/ResearchPage'
import { InsightsPage } from '@/pages/insights/InsightsPage'
import { ScriptStudioPage } from '@/pages/scripts/ScriptStudioPage'
import { VideoProductionPage } from '@/pages/videos/VideoProductionPage'
import { WorkflowPage } from '@/pages/workflow/WorkflowPage'
import { AssetsPage } from '@/pages/assets/AssetsPage'
import { SettingsPage } from '@/pages/settings/SettingsPage'
import { LogsPage } from '@/pages/logs/LogsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Studio App Routes */}
          <Route path="/" element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="campaigns" element={<CampaignsPage />} />
            <Route path="campaigns/:id" element={<CampaignDetailPage />} />
            <Route path="agents" element={<AgentCommandCenterPage />} />
            <Route path="research" element={<ResearchPage />} />
            <Route path="insights" element={<InsightsPage />} />
            <Route path="scripts" element={<ScriptStudioPage />} />
            <Route path="videos" element={<VideoProductionPage />} />
            <Route path="workflow" element={<WorkflowPage />} />
            <Route path="assets" element={<AssetsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="logs" element={<LogsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
