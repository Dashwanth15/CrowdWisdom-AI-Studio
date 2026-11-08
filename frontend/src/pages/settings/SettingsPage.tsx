import React, { useState, useEffect } from 'react'
import {
  Settings2,
  Shield,
  Key,
  CheckCircle2,
  XCircle,
  Play,
  RotateCw,
  Cpu,
  Search,
  Clapperboard,
  Lock,
  ExternalLink,
} from 'lucide-react'
import { integrationsApi } from '@/lib/api'
import { Integration } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { getStatusColor, formatRelativeTime } from '@/lib/utils'
import toast from 'react-hot-toast'

export const SettingsPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [keyInputs, setKeyInputs] = useState<Record<string, string>>({})
  const [modelInputs, setModelInputs] = useState<Record<string, string>>({})
  const [testingProvider, setTestingProvider] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadIntegrations()
  }, [])

  const loadIntegrations = async () => {
    setIsLoading(true)
    try {
      const res = await integrationsApi.list()
      setIntegrations(res.data)
      // Populate models
      const models: Record<string, string> = {}
      res.data.forEach((int: Integration) => {
        if (int.model_name) models[int.provider_name] = int.model_name
      })
      setModelInputs(models)
    } catch (err) {
      toast.error('Failed to load integration configurations')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async (provider: string) => {
    const key = keyInputs[provider]
    const model = modelInputs[provider]

    try {
      await integrationsApi.update(provider, {
        api_key: key || undefined,
        model_name: model || undefined,
        is_active: true,
      })
      toast.success(`${provider} configuration updated!`)
      setKeyInputs((prev) => ({ ...prev, [provider]: '' }))
      loadIntegrations()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update credentials')
    }
  }

  const handleTestConnection = async (provider: string) => {
    setTestingProvider(provider)
    try {
      const res = await integrationsApi.test(provider)
      if (res.data.success) {
        toast.success(`Connection to ${provider} verified successfully!`)
      } else {
        toast.error(`Connection test failed: ${res.data.result?.error || 'Unknown error'}`)
      }
      loadIntegrations()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Connection test failed')
    } finally {
      setTestingProvider(null)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#C5A46D] px-2 py-0.5 rounded bg-[#C5A46D]/10 border border-[#C5A46D]/20">
              Credentials & Infrastructure
            </span>
            <span className="text-xs text-[#727B89] font-mono">• Multi-Provider Gateway</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <Settings2 className="h-6 w-6 text-[#547DB8]" />
            Integrations & API Configuration
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Configure LLM inference, Meta Ads research scrapers, and OpenMontage video engine credentials.
          </p>
        </div>
      </div>

      {/* Security Banner */}
      <div className="p-3.5 rounded-xl bg-[#101216] border border-[#292E37] text-xs flex items-start gap-3">
        <Lock className="h-4 w-4 text-[#547DB8] flex-shrink-0 mt-0.5" />
        <div className="space-y-0.5 text-[#A0A7B2]">
          <span className="font-semibold text-[#7898C4] block">
            Zero-Knowledge Server-Side Cryptographic Storage:
          </span>
          <p className="text-[11px] leading-relaxed">
            All API credentials are encrypted with symmetric Fernet keys derived from environment secrets stored outside MongoDB.
            Raw credentials are never emitted to the React frontend or logged in plain text.
          </p>
        </div>
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {integrations.map((int) => (
          <Card key={int.id} className="border-[#292E37] bg-[#15191F] flex flex-col justify-between hover:border-[#547DB8]/40 transition-colors">
            <CardHeader className="pb-3 border-b border-[#292E37]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {int.category === 'llm' && <Cpu className="h-4 w-4 text-[#C5A46D]" />}
                  {int.category === 'research' && <Search className="h-4 w-4 text-[#547DB8]" />}
                  {int.category === 'video' && <Clapperboard className="h-4 w-4 text-[#7898C4]" />}
                  <CardTitle className="text-sm font-semibold text-[#F2F3F5]">{int.display_name}</CardTitle>
                </div>
                <Badge className={getStatusColor(int.status)}>
                  {int.status}
                </Badge>
              </div>
              <CardDescription className="text-[11px] font-mono capitalize text-[#727B89]">
                Category: {int.category} • Provider: {int.provider_name}
              </CardDescription>
            </CardHeader>

            <CardContent className="p-4 space-y-3">
              {/* Masked Key Display */}
              <div className="space-y-1">
                <Label className="text-xs text-[#A0A7B2]">Active Key Fingerprint</Label>
                <div className="font-mono text-xs text-[#F2F3F5] p-2 rounded-md bg-[#101216] border border-[#292E37]">
                  {int.api_key_masked || 'No key configured yet'}
                </div>
              </div>

              {/* Set/Update Key Input */}
              <div className="space-y-1">
                <Label className="text-xs text-[#A0A7B2]">Update API Secret</Label>
                <Input
                  type="password"
                  placeholder="Paste new API key to update..."
                  className="text-xs font-mono bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                  value={keyInputs[int.provider_name] || ''}
                  onChange={(e) =>
                    setKeyInputs((prev) => ({ ...prev, [int.provider_name]: e.target.value }))
                  }
                />
              </div>

              {/* Model selection if LLM */}
              {int.category === 'llm' && (
                <div className="space-y-1">
                  <Label className="text-xs text-[#A0A7B2]">Selected Model Identifier</Label>
                  <Input
                    className="text-xs font-mono bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                    value={modelInputs[int.provider_name] || ''}
                    placeholder="e.g. meta-llama/llama-3.1-70b-instruct"
                    onChange={(e) =>
                      setModelInputs((prev) => ({
                        ...prev,
                        [int.provider_name]: e.target.value,
                      }))
                    }
                  />
                </div>
              )}

              {int.last_tested_at && (
                <p className="text-[10px] text-[#727B89] font-mono">
                  Last verified: {formatRelativeTime(int.last_tested_at)}
                </p>
              )}
            </CardContent>

            <CardFooter className="p-4 pt-0 border-t border-[#292E37] flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                className="text-xs h-8 border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]"
                disabled={testingProvider === int.provider_name || !int.api_key_configured}
                onClick={() => handleTestConnection(int.provider_name)}
              >
                {testingProvider === int.provider_name ? (
                  <>
                    <RotateCw className="h-3 w-3 mr-1 animate-spin" /> Verifying...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-3 w-3 mr-1 text-[#36B58F]" /> Test Connection
                  </>
                )}
              </Button>

              <Button
                variant="brand"
                size="sm"
                className="text-xs h-8 bg-[#547DB8] hover:bg-[#436494] text-white font-medium"
                onClick={() => handleSave(int.provider_name)}
              >
                Save Settings
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}
