import React, { useState, useEffect } from 'react'
import { Terminal, RefreshCw, Filter, Search, ShieldAlert, Cpu } from 'lucide-react'
import { agentsApi } from '@/lib/api'
import { AgentExecution } from '@/types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { getStatusColor, formatRelativeTime } from '@/lib/utils'
import toast from 'react-hot-toast'

export const LogsPage: React.FC = () => {
  const [executions, setExecutions] = useState<AgentExecution[]>([])
  const [search, setSearch] = useState('')
  const [filterAgent, setFilterAgent] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadLogs()
  }, [])

  const loadLogs = async () => {
    setIsLoading(true)
    try {
      const res = await agentsApi.listExecutions({ limit: 100 })
      setExecutions(res.data)
    } catch (err) {
      toast.error('Failed to load system execution logs')
    } finally {
      setIsLoading(false)
    }
  }

  const filtered = executions.filter((exec) => {
    const matchesAgent = filterAgent === 'all' || exec.agent_type === filterAgent
    const matchesSearch =
      exec.task_name.toLowerCase().includes(search.toLowerCase()) ||
      exec.id.toLowerCase().includes(search.toLowerCase()) ||
      (exec.error_message && exec.error_message.toLowerCase().includes(search.toLowerCase()))
    return matchesAgent && matchesSearch
  })

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#C5A46D] px-2 py-0.5 rounded bg-[#C5A46D]/10 border border-[#C5A46D]/20">
              Observability
            </span>
            <span className="text-xs text-[#727B89] font-mono">• Execution Telemetry Stream</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <Terminal className="h-6 w-6 text-[#547DB8]" />
            Execution Logs & System Observability
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Audit trail of autonomous agent tasks, tool invocations, and error telemetry.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={loadLogs} className="text-xs h-8 border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]">
          <RefreshCw className="h-3.5 w-3.5 mr-1.5" /> Refresh Telemetry
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#727B89]" />
          <Input
            placeholder="Search task name, execution ID, or error messages..."
            className="pl-9 text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5]"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2">
          {['all', 'ads_manager', 'script', 'video_production'].map((ag) => {
            const isActive = filterAgent === ag
            return (
              <Button
                key={ag}
                variant={isActive ? 'secondary' : 'ghost'}
                size="sm"
                className={`h-8 text-xs capitalize border ${
                  isActive
                    ? 'bg-[#1B2028] text-[#F2F3F5] border-[#547DB8]/50'
                    : 'border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]'
                }`}
                onClick={() => setFilterAgent(ag)}
              >
                {ag.replace('_', ' ')}
              </Button>
            )
          })}
        </div>
      </div>

      {/* Terminal Log Stream Window */}
      <Card className="border-[#292E37] bg-[#15191F] overflow-hidden">
        <CardHeader className="py-3 px-4 border-b border-[#292E37] bg-[#101216] flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-[#D66C73]/80" />
              <div className="h-2.5 w-2.5 rounded-full bg-[#D9A94F]/80" />
              <div className="h-2.5 w-2.5 rounded-full bg-[#36B58F]/80" />
            </div>
            <span className="text-xs font-mono text-[#727B89] ml-2">
              crowdwisdom-orchestrator.telemetry.stream
            </span>
          </div>

          <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] font-mono text-[10px] border border-[#292E37] bg-[#10141C] text-[#8E9EB5] tabular-nums">
            {filtered.length} RECORDED RUNS
          </span>
        </CardHeader>

        <CardContent className="p-4 font-mono text-xs space-y-3 max-h-[600px] overflow-y-auto bg-[#080A0F]">
          {filtered.length === 0 ? (
            <div className="text-center py-12 text-[#727B89]">
              No matching log records found.
            </div>
          ) : (
            filtered.map((item) => (
              <div
                key={item.id}
                className="p-3 rounded-lg bg-[#101216] border border-[#292E37] space-y-1.5 hover:border-[#547DB8]/40 transition-colors"
              >
                <div className="flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="text-[#727B89]">[{item.created_at.slice(0, 19)}]</span>
                    <span className="font-semibold text-[#547DB8] capitalize">
                      [{item.agent_type.replace('_', ' ')}]
                    </span>
                    <span className="text-[#F2F3F5] font-semibold">{item.task_name}</span>
                  </div>
                  <Badge className={getStatusColor(item.status)}>{item.status}</Badge>
                </div>

                <div className="text-[11px] text-[#727B89] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>Execution ID: {item.id}</span>
                    {item.execution_mode === 'native_hermes' ? (
                      <span className="inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded-[3px] text-[9px] font-mono bg-[#10141C] text-[#D8DCE4] border border-[#232B38]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" /> HERMES NATIVE
                      </span>
                    ) : item.execution_mode === 'llm_fallback' ? (
                      <span className="inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded-[3px] text-[9px] font-mono bg-[#10141C] text-[#D8DCE4] border border-[#232B38]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#D9A94F]" /> LLM FALLBACK
                      </span>
                    ) : item.status === 'failed' ? (
                      <span className="inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded-[3px] text-[9px] font-mono bg-[#10141C] text-[#D8DCE4] border border-[#232B38]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#D66C73]" /> FAILED
                      </span>
                    ) : null}
                  </div>
                  <span className="tabular-nums">Duration: {item.duration_seconds ? `${item.duration_seconds.toFixed(2)}s` : 'N/A'}</span>
                </div>

                {item.error_message && (
                  <div className="p-2 rounded bg-[#1F1416] border border-[#D66C73]/30 text-[#D66C73] text-[11px]">
                    <span className="font-bold">ERROR: </span>
                    {item.error_message}
                  </div>
                )}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}
