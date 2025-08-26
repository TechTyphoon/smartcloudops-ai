"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useWebSocket } from "./use-websocket"
import { apiService } from "@/lib/api"

interface MetricData {
  timestamp: string
  value: number
  status: "healthy" | "warning" | "critical"
}

interface SystemMetrics {
  cpu: MetricData
  memory: MetricData
  disk: MetricData
  network: MetricData
}

interface UseRealTimeMetricsConfig {
  enableWebSocket?: boolean
  fallbackInterval?: number
  retryDelay?: number
}

export function useRealTimeMetrics(config: UseRealTimeMetricsConfig = {}) {
  const { enableWebSocket = true, fallbackInterval = 5000, retryDelay = 1000 } = config

  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
    memory: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
    disk: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
    network: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
  })

  const [connectionStatus, setConnectionStatus] = useState<"connected" | "connecting" | "disconnected" | "fallback">(
    "disconnected",
  )

  const fallbackIntervalRef = useRef<NodeJS.Timeout>()
  const retryTimeoutRef = useRef<NodeJS.Timeout>()

  const webSocket = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:3001/metrics",
    reconnectInterval: retryDelay,
    maxReconnectAttempts: 3,
    heartbeatInterval: 30000,
  })

  const generateMockMetrics = useCallback(async (): Promise<SystemMetrics> => {
    try {
      return await apiService.getSystemMetrics()
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
      const now = new Date().toISOString()
      return {
        cpu: { timestamp: now, value: 0, status: "healthy" },
        memory: { timestamp: now, value: 0, status: "healthy" },
        disk: { timestamp: now, value: 0, status: "healthy" },
        network: { timestamp: now, value: 0, status: "healthy" },
      }
    }
  }, [])

  const startFallbackPolling = useCallback(() => {
    if (fallbackIntervalRef.current) {
      clearInterval(fallbackIntervalRef.current)
    }

    setConnectionStatus("fallback")
    fallbackIntervalRef.current = setInterval(async () => {
      const newMetrics = await generateMockMetrics()
      setMetrics(newMetrics)
    }, fallbackInterval)
  }, [generateMockMetrics, fallbackInterval])

  const stopFallbackPolling = useCallback(() => {
    if (fallbackIntervalRef.current) {
      clearInterval(fallbackIntervalRef.current)
      fallbackIntervalRef.current = undefined
    }
  }, [])

  useEffect(() => {
    if (!enableWebSocket) {
      startFallbackPolling()
      return
    }

    const removeHandler = webSocket.addMessageHandler((data) => {
      if (data.type === "metrics") {
        setMetrics(data.payload)
      }
    })

    return removeHandler
  }, [enableWebSocket, webSocket.addMessageHandler, startFallbackPolling])

  useEffect(() => {
    if (!enableWebSocket) return

    if (webSocket.isConnected) {
      setConnectionStatus("connected")
      stopFallbackPolling()
    } else if (webSocket.isConnecting) {
      setConnectionStatus("connecting")
    } else if (webSocket.error && webSocket.reconnectAttempts >= 3) {
      // Fallback to polling after max reconnect attempts
      startFallbackPolling()
    } else {
      setConnectionStatus("disconnected")
    }
  }, [
    enableWebSocket,
    webSocket.isConnected,
    webSocket.isConnecting,
    webSocket.error,
    webSocket.reconnectAttempts,
    startFallbackPolling,
    stopFallbackPolling,
  ])

  useEffect(() => {
    if (webSocket.isConnected) {
      webSocket.sendMessage({ type: "subscribe", channel: "metrics" })
    }
  }, [webSocket.isConnected, webSocket.sendMessage])

  // Cleanup
  useEffect(() => {
    return () => {
      stopFallbackPolling()
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [stopFallbackPolling])

  const refreshMetrics = useCallback(async () => {
    if (webSocket.isConnected) {
      webSocket.sendMessage({ type: "refresh", channel: "metrics" })
    } else {
      const newMetrics = await generateMockMetrics()
      setMetrics(newMetrics)
    }
  }, [webSocket.isConnected, webSocket.sendMessage, generateMockMetrics])

  return {
    metrics,
    connectionStatus,
    refreshMetrics,
    isRealTime: connectionStatus === "connected",
    error: webSocket.error,
  }
}
