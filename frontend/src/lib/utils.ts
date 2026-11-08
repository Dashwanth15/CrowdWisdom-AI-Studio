import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { formatDistanceToNow, format } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  try {
    return format(new Date(date), 'MMM d, yyyy')
  } catch {
    return String(date)
  }
}

export function formatDateTime(date: string | Date): string {
  try {
    return format(new Date(date), 'MMM d, yyyy h:mm a')
  } catch {
    return String(date)
  }
}

export function formatRelativeTime(date: string | Date): string {
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true })
  } catch {
    return 'recently'
  }
}

export function formatDuration(seconds: number): string {
  if (!seconds || seconds <= 0) return '0s'
  if (seconds < 60) return `${Math.round(seconds)}s`
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return `${mins}m ${secs}s`
}

export function formatFileSize(bytes: number): string {
  if (!bytes || bytes <= 0) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function getStatusColor(status: string): string {
  const statusConfig: Record<string, string> = {
    // Green / active / completed / approved / verified
    completed:
      "bg-[#092319] border border-[#14533D] text-[#34D399] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#10B981] before:shadow-[0_0_6px_#10B981]",
    active:
      "bg-[#0A2238] border border-[#144872] text-[#38BDF8] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#0EA5E9] before:shadow-[0_0_6px_#0EA5E9]",
    approved:
      "bg-[#092319] border border-[#14533D] text-[#34D399] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#10B981] before:shadow-[0_0_6px_#10B981]",
    configured:
      "bg-[#0A2238] border border-[#144872] text-[#38BDF8] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#0EA5E9] before:shadow-[0_0_6px_#0EA5E9]",
    verified:
      "bg-[#092319] border border-[#14533D] text-[#34D399] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#10B981] before:shadow-[0_0_6px_#10B981]",

    // Blue / running / processing / in_production
    running:
      "bg-[#0A2238] border border-[#144872] text-[#38BDF8] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#0EA5E9] before:animate-pulse before:shadow-[0_0_6px_#0EA5E9]",
    processing:
      "bg-[#0A2238] border border-[#144872] text-[#38BDF8] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#0EA5E9] before:animate-pulse before:shadow-[0_0_6px_#0EA5E9]",
    composing:
      "bg-[#0A2238] border border-[#144872] text-[#38BDF8] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#0EA5E9] before:animate-pulse before:shadow-[0_0_6px_#0EA5E9]",
    rendering:
      "bg-[#0A2238] border border-[#144872] text-[#38BDF8] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#0EA5E9] before:animate-pulse before:shadow-[0_0_6px_#0EA5E9]",
    in_production:
      "bg-[#0A2238] border border-[#144872] text-[#38BDF8] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#0EA5E9] before:animate-pulse before:shadow-[0_0_6px_#0EA5E9]",

    // Amber / pending / queued / review
    pending:
      "bg-[#251B0B] border border-[#533B18] text-[#FBBF24] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#F59E0B] before:shadow-[0_0_6px_#F59E0B]",
    pending_approval:
      "bg-[#251B0B] border border-[#533B18] text-[#FBBF24] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#F59E0B] before:shadow-[0_0_6px_#F59E0B]",
    awaiting_approval:
      "bg-[#251B0B] border border-[#533B18] text-[#FBBF24] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#F59E0B] before:shadow-[0_0_6px_#F59E0B]",
    queued:
      "bg-[#251B0B] border border-[#533B18] text-[#FBBF24] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#F59E0B] before:shadow-[0_0_6px_#F59E0B]",
    generating:
      "bg-[#251B0B] border border-[#533B18] text-[#FBBF24] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#F59E0B] before:animate-pulse before:shadow-[0_0_6px_#F59E0B]",
    paused:
      "bg-[#251B0B] border border-[#533B18] text-[#FBBF24] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#F59E0B]",

    // Red / failed / rejected / error
    failed:
      "bg-[#260E12] border border-[#5A1C24] text-[#F87171] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#EF4444] before:shadow-[0_0_6px_#EF4444]",
    rejected:
      "bg-[#260E12] border border-[#5A1C24] text-[#F87171] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#EF4444] before:shadow-[0_0_6px_#EF4444]",
    error:
      "bg-[#260E12] border border-[#5A1C24] text-[#F87171] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#EF4444] before:shadow-[0_0_6px_#EF4444]",

    // Gray / draft / archived / cancelled / unconfigured
    draft:
      "bg-[#161D2B] border border-[#2B3952] text-[#CBD5E1] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#94A3B8]",
    archived:
      "bg-[#161D2B] border border-[#2B3952] text-[#CBD5E1] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#94A3B8]",
    cancelled:
      "bg-[#161D2B] border border-[#2B3952] text-[#CBD5E1] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#94A3B8]",
    unconfigured:
      "bg-[#161D2B] border border-[#2B3952] text-[#CBD5E1] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#94A3B8]",
  }

  return (
    statusConfig[status] ||
    "bg-[#161D2B] border border-[#2B3952] text-[#CBD5E1] text-[10px] font-mono tracking-wider uppercase font-semibold rounded-[4px] px-2.5 py-0.5 inline-flex items-center shadow-xs before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5 before:bg-[#94A3B8]"
  )
}

function getMediaHostPrefix(): string {
  const envApiUrl = import.meta.env.VITE_API_BASE_URL
  if (envApiUrl && typeof envApiUrl === 'string' && (envApiUrl.startsWith('http://') || envApiUrl.startsWith('https://'))) {
    try {
      const urlObj = new URL(envApiUrl)
      return `${urlObj.protocol}//${urlObj.host}`
    } catch {
      // Fall through
    }
  }
  return ''
}

export function resolveMediaUrl(url: string | undefined | null): string {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('blob:')) return url

  // Standardize backslashes from Windows paths and trim whitespace
  const cleanUrl = url.replace(/\\/g, '/').trim()
  const prefix = getMediaHostPrefix()

  let path = ''
  // Handle bare filenames or any string referencing asset_
  if (cleanUrl.includes('asset_')) {
    const filename = cleanUrl.split('/').pop()
    path = `/media/assets/${filename}`
  } else if (cleanUrl.endsWith('.mp4')) {
    const filename = cleanUrl.split('/').pop()
    path = `/media/videos/${filename}`
  } else if (cleanUrl.startsWith('media/')) {
    path = `/${cleanUrl}`
  } else {
    path = cleanUrl.startsWith('/') ? cleanUrl : `/${cleanUrl}`
  }

  return prefix ? `${prefix}${path}` : path
}
