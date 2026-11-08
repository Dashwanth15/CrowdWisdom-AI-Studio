import React, { useState, useEffect } from 'react'
import {
  FolderOpen,
  Film,
  FileText,
  Image as ImageIcon,
  Download,
  Trash2,
  ExternalLink,
  Filter,
} from 'lucide-react'
import { assetsApi } from '@/lib/api'
import { MediaAsset, AssetType } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatFileSize, formatRelativeTime, resolveMediaUrl } from '@/lib/utils'
import { CrowdWisdomLogo } from '@/components/branding'
import toast from 'react-hot-toast'

export const AssetsPage: React.FC = () => {
  const [assets, setAssets] = useState<MediaAsset[]>([])
  const [filterType, setFilterType] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadAssets()
  }, [])

  const loadAssets = async () => {
    setIsLoading(true)
    try {
      const res = await assetsApi.list({ limit: 100 })
      setAssets(res.data)
    } catch (err) {
      toast.error('Failed to load asset library')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this media asset?')) return
    try {
      await assetsApi.delete(id)
      toast.success('Asset deleted')
      loadAssets()
    } catch (err) {
      toast.error('Failed to delete asset')
    }
  }

  const filteredAssets = assets.filter((a) => {
    if (filterType === 'all') return true
    return a.asset_type === filterType
  })

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#C5A46D] px-2 py-0.5 rounded bg-[#C5A46D]/10 border border-[#C5A46D]/20">
              Media Vault
            </span>
            <span className="text-xs text-[#727B89] font-mono">• Direct S3 & Local Media Storage</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <FolderOpen className="h-6 w-6 text-[#547DB8]" />
            Creative Assets Library
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Centralized media storage for rendered MP4 advertisements, storyboards, voiceovers, and research dumps.
          </p>
        </div>
      </div>

      {/* Official Brand Identity Kit Card */}
      <Card className="border-[#292E37] bg-[#12161F] shadow-lg overflow-hidden">
        <div className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#292E37]/60">
          <div className="flex items-center gap-3">
            <CrowdWisdomLogo variant="badge" size="sm" />
            <div>
              <h2 className="text-sm font-semibold text-[#F2F3F5] tracking-tight">
                Official CrowdWisdom Brand Identity & Media Kit
              </h2>
              <p className="text-xs text-[#727B89] font-mono">
                Official Bears & Bulls Tug-of-War Vector & Raster Assets (PNG, WebP, SVG, ICO)
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <a href="/crowdwisdom_logo_symbol.png" download="crowdwisdom_symbol.png">
              <Button variant="outline" size="sm" className="h-8 text-xs border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]">
                <Download className="h-3.5 w-3.5 mr-1.5" />
                Bears & Bulls Symbol
              </Button>
            </a>
            <a href="/crowdwisdom_logo_badge.png" download="crowdwisdom_badge.png">
              <Button variant="brand" size="sm" className="h-8 text-xs">
                <Download className="h-3.5 w-3.5 mr-1.5" />
                Institutional Badge
              </Button>
            </a>
          </div>
        </div>
      </Card>

      {/* Asset Type Filter Pills */}
      <div className="flex items-center gap-2 pb-2 overflow-x-auto">
        {['all', 'video', 'thumbnail', 'image', 'script_json'].map((type) => {
          const isActive = filterType === type
          return (
            <Button
              key={type}
              variant={isActive ? 'secondary' : 'ghost'}
              size="sm"
              className={`h-8 text-xs capitalize border ${
                isActive
                  ? 'bg-[#1B2028] text-[#F2F3F5] border-[#547DB8]/50'
                  : 'border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]'
              }`}
              onClick={() => setFilterType(type)}
            >
              {type.replace('_', ' ')}
            </Button>
          )
        })}
      </div>

      {/* Assets Grid */}
      {filteredAssets.length === 0 ? (
        <Card className="p-12 text-center border-dashed border-[#292E37] bg-[#15191F]">
          <FolderOpen className="h-8 w-8 text-[#727B89] mx-auto mb-2 opacity-50" />
          <p className="text-xs text-[#A0A7B2]">
            No assets found for the selected category. Generated commercials will automatically appear here.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAssets.map((asset) => (
            <Card key={asset.id} className="border-[#292E37] bg-[#15191F] flex flex-col justify-between overflow-hidden hover:border-[#547DB8]/40 transition-colors">
              <div className="aspect-video bg-[#080A0F] flex items-center justify-center relative border-b border-[#292E37]">
                {asset.asset_type === 'video' ? (
                  <Film className="h-10 w-10 text-[#547DB8] opacity-80" />
                ) : (
                  <ImageIcon className="h-10 w-10 text-[#727B89] opacity-60" />
                )}
                <span className="absolute top-2 right-2 px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono capitalize bg-[#10141C]/90 backdrop-blur border border-[#232B38] text-[#8E9EB5]">
                  {asset.asset_type}
                </span>
              </div>

              <CardContent className="p-4 space-y-2">
                <h4 className="text-xs font-semibold text-[#F2F3F5] truncate">
                  {asset.filename}
                </h4>

                <div className="flex items-center justify-between text-[10px] text-[#727B89] font-mono tabular-nums">
                  <span>
                    {asset.file_size_bytes ? formatFileSize(asset.file_size_bytes) : '-'}
                  </span>
                  <span>{formatRelativeTime(asset.created_at)}</span>
                </div>
              </CardContent>

              <CardFooter className="p-4 pt-0 border-t border-[#292E37] flex items-center justify-between">
                {asset.url ? (
                  <a href={resolveMediaUrl(asset.url)} download={asset.filename}>
                    <Button variant="outline" size="sm" className="h-7 text-xs border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]">
                      <Download className="h-3 w-3 mr-1" /> Download
                    </Button>
                  </a>
                ) : (
                  <span />
                )}

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 text-[#727B89] hover:text-[#D66C73] hover:bg-[#D66C73]/10"
                  onClick={() => handleDelete(asset.id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
