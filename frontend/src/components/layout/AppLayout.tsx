import React, { useEffect } from 'react'
import { Outlet, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { useAuthStore } from '@/stores/authStore'
import { wsManager } from '@/lib/websocket'

export const AppLayout: React.FC = () => {
  const { isAuthenticated, token } = useAuthStore()

  useEffect(() => {
    if (token) {
      wsManager.connect(token)
    }
  }, [token])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#080A0F] text-[#F2F3F5]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#080A0F]">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-[#080A0F]">
          <Outlet />
        </main>
      </div>
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: 'bg-[#15191F] text-[#F2F3F5] border border-[#292E37] text-xs shadow-xl rounded-lg font-sans',
          duration: 4000,
          style: {
            background: '#15191F',
            color: '#F2F3F5',
            border: '1px solid #292E37',
          },
        }}
      />
    </div>
  )
}
