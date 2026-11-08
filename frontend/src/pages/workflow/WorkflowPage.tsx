import React, { useState, useEffect } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import {
  KanbanSquare,
  Workflow as WorkflowIcon,
  Bot,
  Clock,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  RefreshCw,
  Plus,
} from 'lucide-react'
import { workflowApi, campaignsApi } from '@/lib/api'
import { WorkflowTask, Campaign, TaskStatus } from '@/types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { getStatusColor, formatRelativeTime } from '@/lib/utils'
import toast from 'react-hot-toast'

const COLUMNS: { id: TaskStatus; title: string; borderColor: string; badgeColor: string }[] = [
  { id: 'pending', title: 'Pending', borderColor: 'border-[#292E37]', badgeColor: 'bg-[#727B89]/15 text-[#A0A7B2] border-[#292E37]' },
  { id: 'running', title: 'In Execution', borderColor: 'border-[#547DB8]/50', badgeColor: 'bg-[#547DB8]/15 text-[#7898C4] border-[#547DB8]/30' },
  { id: 'awaiting_approval', title: 'Awaiting Gate', borderColor: 'border-[#C5A46D]/50', badgeColor: 'bg-[#C5A46D]/15 text-[#C5A46D] border-[#C5A46D]/30' },
  { id: 'completed', title: 'Completed', borderColor: 'border-[#36B58F]/50', badgeColor: 'bg-[#36B58F]/15 text-[#36B58F] border-[#36B58F]/30' },
  { id: 'failed', title: 'Failed / Paused', borderColor: 'border-[#D66C73]/50', badgeColor: 'bg-[#D66C73]/15 text-[#D66C73] border-[#D66C73]/30' },
]

// React Flow Visual Pipeline Nodes (Midnight Executive styling)
const initialNodes: Node[] = [
  {
    id: '1',
    data: { label: '01. Campaign Creation & Audience Profile' },
    position: { x: 50, y: 150 },
    style: { background: '#15191F', color: '#F2F3F5', border: '1px solid #292E37', borderRadius: '8px', padding: '12px', fontSize: '11px', fontWeight: 600 },
  },
  {
    id: '2',
    data: { label: '02. Ads Manager Agent (Apify Meta Ads Scraper)' },
    position: { x: 350, y: 150 },
    style: { background: '#15191F', color: '#F2F3F5', border: '1px solid #547DB8', borderRadius: '8px', padding: '12px', fontSize: '11px', fontWeight: 600 },
  },
  {
    id: '3',
    data: { label: '03. Creative Intelligence Engine [Gate 1: Brief Sign-Off]' },
    position: { x: 680, y: 150 },
    style: { background: '#1B2028', color: '#7898C4', border: '1px solid #547DB8', borderRadius: '8px', padding: '12px', fontSize: '11px', fontWeight: 600 },
  },
  {
    id: '4',
    data: { label: '04. Script Agent (Storyboard Generation)' },
    position: { x: 1020, y: 150 },
    style: { background: '#15191F', color: '#F2F3F5', border: '1px solid #292E37', borderRadius: '8px', padding: '12px', fontSize: '11px', fontWeight: 600 },
  },
  {
    id: '5',
    data: { label: '05. Human Approval Checkpoint [Gate 2: Storyboard Sign-off]' },
    position: { x: 680, y: 320 },
    style: { background: '#1F1A12', color: '#C5A46D', border: '2px dashed #C5A46D', borderRadius: '8px', padding: '12px', fontSize: '11px', fontWeight: 700 },
  },
  {
    id: '6',
    data: { label: '06. Video Production Agent (OpenMontage / MoviePy)' },
    position: { x: 350, y: 320 },
    style: { background: '#15191F', color: '#F2F3F5', border: '1px solid #547DB8', borderRadius: '8px', padding: '12px', fontSize: '11px', fontWeight: 600 },
  },
  {
    id: '7',
    data: { label: '07. High-Definition MP4 Video Advertisement Output' },
    position: { x: 50, y: 320 },
    style: { background: '#0D1E18', color: '#36B58F', border: '1px solid #36B58F', borderRadius: '8px', padding: '12px', fontSize: '11px', fontWeight: 700 },
  },
]

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#547DB8' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#547DB8' } },
  { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: '#547DB8' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#547DB8' } },
  { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#547DB8' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#547DB8' } },
  { id: 'e4-5', source: '4', target: '5', animated: true, style: { stroke: '#C5A46D' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#C5A46D' } },
  { id: 'e5-6', source: '5', target: '6', animated: true, style: { stroke: '#547DB8' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#547DB8' } },
  { id: 'e6-7', source: '6', target: '7', animated: true, style: { stroke: '#36B58F' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#36B58F' } },
]

export const WorkflowPage: React.FC = () => {
  const [tasks, setTasks] = useState<WorkflowTask[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [selectedCampaign, setSelectedCampaign] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadWorkflow()
  }, [])

  const loadWorkflow = async () => {
    setIsLoading(true)
    try {
      const [tasksRes, campsRes] = await Promise.all([
        workflowApi.listTasks({ limit: 100 }),
        campaignsApi.list(),
      ])
      setTasks(tasksRes.data)
      setCampaigns(campsRes.data)
    } catch (err) {
      toast.error('Failed to load workflow state')
    } finally {
      setIsLoading(false)
    }
  }

  const filteredTasks = tasks.filter((t) => {
    if (selectedCampaign === 'all') return true
    return t.campaign_id === selectedCampaign
  })

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#C5A46D] px-2 py-0.5 rounded bg-[#C5A46D]/10 border border-[#C5A46D]/20">
              Pipeline Topology
            </span>
            <span className="text-xs text-[#727B89] font-mono">• 7-Stage Autonomous State Machine</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <WorkflowIcon className="h-6 w-6 text-[#547DB8]" />
            Visual Workflow & Hermes Kanban
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Real-time pipeline orchestration, task dependencies, and human-in-the-loop approval gates.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {campaigns.length > 0 && (
            <select
              className="bg-[#101216] border border-[#292E37] rounded-md px-3 py-1.5 text-xs font-medium text-[#F2F3F5] outline-none focus:border-[#547DB8]"
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
            >
              <option value="all">All Campaigns</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          )}

          <Button variant="outline" size="sm" onClick={loadWorkflow} className="text-xs h-8 border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]">
            <RefreshCw className="h-3.5 w-3.5 mr-1" /> Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="kanban" className="space-y-4">
        <TabsList className="bg-[#101216] border border-[#292E37]">
          <TabsTrigger value="kanban" className="text-xs data-[state=active]:bg-[#1B2028] data-[state=active]:text-[#F2F3F5]">
            <KanbanSquare className="h-3.5 w-3.5 mr-1.5" />
            Task Kanban Board
          </TabsTrigger>
          <TabsTrigger value="diagram" className="text-xs data-[state=active]:bg-[#1B2028] data-[state=active]:text-[#F2F3F5]">
            <WorkflowIcon className="h-3.5 w-3.5 mr-1.5" />
            Interactive Node Workflow
          </TabsTrigger>
        </TabsList>

        {/* --- Kanban Board View --- */}
        <TabsContent value="kanban">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            {COLUMNS.map((col) => {
              const colTasks = filteredTasks.filter((t) => t.status === col.id)
              return (
                <div
                  key={col.id}
                  className={`flex flex-col rounded-xl border bg-[#15191F] p-3 min-h-[500px] ${col.borderColor}`}
                >
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#292E37]">
                    <span className="text-xs font-semibold text-[#F2F3F5]">{col.title}</span>
                    <span className="inline-flex items-center px-1.5 py-0.2 rounded-[3px] text-[10px] font-mono tabular-nums bg-[#10141C] border border-[#232B38] text-[#8E9EB5]">
                      {colTasks.length}
                    </span>
                  </div>

                  <div className="space-y-2 flex-1 overflow-y-auto">
                    {colTasks.length === 0 ? (
                      <div className="h-24 flex items-center justify-center text-[11px] text-[#727B89] border border-dashed border-[#292E37] rounded-lg">
                        No tasks
                      </div>
                    ) : (
                      colTasks.map((t) => (
                        <div
                          key={t.id}
                          className="p-3 rounded-lg bg-[#101216] border border-[#292E37] text-xs space-y-2 hover:border-[#547DB8]/40 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-[#F2F3F5] text-[11px] line-clamp-1">
                              {t.task_name}
                            </span>
                            {t.agent_type && (
                              <span className="inline-flex items-center px-1.5 py-0.2 rounded-[3px] text-[9px] font-mono capitalize bg-[#10141C] text-[#8E9EB5] border border-[#232B38]">
                                {t.agent_type.replace('_', ' ')}
                              </span>
                            )}
                          </div>

                          {t.description && (
                            <p className="text-[11px] text-[#A0A7B2] line-clamp-2">
                              {t.description}
                            </p>
                          )}

                          <div className="flex items-center justify-between text-[10px] text-[#727B89] pt-1 border-t border-[#292E37] font-mono tabular-nums">
                            <span>Pri: {t.priority}</span>
                            <span>{formatRelativeTime(t.created_at)}</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </TabsContent>

        {/* --- React Flow Node View --- */}
        <TabsContent value="diagram">
          <Card className="border-[#292E37] overflow-hidden bg-[#15191F]">
            <div className="h-[520px] w-full bg-[#080A0F]">
              <ReactFlow
                nodes={initialNodes}
                edges={initialEdges}
                fitView
              >
                <Background color="#1B2028" gap={16} />
                <Controls />
                <MiniMap
                  nodeStrokeWidth={3}
                  maskColor="rgba(8, 10, 15, 0.7)"
                  style={{ background: '#101216', border: '1px solid #292E37' }}
                />
              </ReactFlow>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
