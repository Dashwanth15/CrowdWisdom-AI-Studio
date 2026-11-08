import { WSEvent } from '@/types'

type EventHandler = (event: WSEvent) => void

class WebSocketManager {
  private ws: WebSocket | null = null
  private clientId: string
  private handlers: Map<string, Set<EventHandler>> = new Map()
  private reconnectTimer: any = null
  private reconnectDelay = 2000
  private maxReconnectDelay = 30000
  private isConnecting = false
  private tokenRejected = false

  constructor() {
    this.clientId = `client_${Date.now()}_${Math.random().toString(36).slice(2)}`
  }

  connect(token?: string): void {
    if (token) {
      this.tokenRejected = false
    }
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) return
    // Don't reconnect if the token was explicitly rejected by the server
    if (this.tokenRejected) return
    this.isConnecting = true

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const tokenParam = token ? `?token=${encodeURIComponent(token)}` : ''
    const url = `${protocol}//${window.location.host}/ws/${this.clientId}${tokenParam}`

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        this.isConnecting = false
        this.reconnectDelay = 2000
        this.emit('connected', { type: 'connected', client_id: this.clientId })
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WSEvent
          this.emit(data.type, data)
          this.emit('*', data)
        } catch (e) {
          console.error('[WS] Failed to parse message:', e)
        }
      }

      this.ws.onclose = (event) => {
        this.isConnecting = false
        // 4001 = server rejected token as invalid/expired — stop reconnecting
        // 4003 = forbidden — also stop
        if (event.code === 4001 || event.code === 4003) {
          this.tokenRejected = true
          console.warn('[WS] Token rejected by server (code', event.code, '). Stopping reconnect. Please log in again.')
          this.emit('token_expired', { type: 'token_expired', message: 'Session expired. Please log in again.' } as any)
          return
        }
        this.scheduleReconnect(token)
      }

      this.ws.onerror = (err) => {
        this.isConnecting = false
      }
    } catch (e) {
      this.isConnecting = false
      this.scheduleReconnect(token)
    }
  }

  private scheduleReconnect(token?: string): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.reconnectTimer = setTimeout(() => {
      this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, this.maxReconnectDelay)
      this.connect(token)
    }, this.reconnectDelay)
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }
  }

  /** Call after a fresh login to reset the token-rejected flag and reconnect */
  reconnectWithToken(token: string): void {
    this.tokenRejected = false
    this.reconnectDelay = 2000
    this.disconnect()
    this.connect(token)
  }

  on(eventType: string, handler: EventHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    this.handlers.get(eventType)!.add(handler)

    return () => {
      this.handlers.get(eventType)?.delete(handler)
    }
  }

  off(eventType: string, handler: EventHandler): void {
    this.handlers.get(eventType)?.delete(handler)
  }

  private emit(eventType: string, data: WSEvent): void {
    this.handlers.get(eventType)?.forEach((handler) => {
      try {
        handler(data)
      } catch (e) {
        console.error('[WS] Handler error:', e)
      }
    })
  }

  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsManager = new WebSocketManager()
export default wsManager
