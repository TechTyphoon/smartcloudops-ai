"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useWebSocket } from "./use-websocket"

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

  // TODO: Replace with real metrics API call
  const fetchRealMetrics = useCallback(async (): Promise<SystemMetrics> => {
    try {
      // const response = await fetch('/api/metrics/current')
      // const data = await response.json()
      // return data
      
      // Placeholder for real API integration
      return {
        cpu: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
        memory: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
        disk: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
        network: { timestamp: new Date().toISOString(), value: 0, status: "healthy" },
      }
    } catch (error) {
      console.error('Failed to fetch real metrics:', error)
      return metrics
    }
  }, [metrics])

  const startFallbackPolling = useCallback(() => {
    if (fallbackIntervalRef.current) {
      clearInterval(fallbackIntervalRef.current)
    }

    setConnectionStatus("fallback")
    fallbackIntervalRef.current = setInterval(async () => {
      const realMetrics = await fetchRealMetrics()
      setMetrics(realMetrics)
    }, fallbackInterval)
  }, [fetchRealMetrics, fallbackInterval])

  const stopFallbackPolling = useCallback(() => {
    if (fallbackIntervalRef.current) {
      clearInterval(fallbackIntervalRef.current)
      fallbackIntervalRef.current = undefined
    }
  }, [])

  useEffect(() => {
    if (!enableWebSocket) {
      startFallbackPolling()
      return () => {
        stopFallbackPolling()
      }
    }

    const removeHandler = webSocket.addMessageHandler((data) => {
      if (data.type === "metrics") {
        setMetrics(data.payload)
      }
    })

    return () => {
      removeHandler()
    }
  }, [enableWebSocket, webSocket.addMessageHandler, startFallbackPolling, stopFallbackPolling])

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

  const refreshMetrics = useCallback(() => {
    if (webSocket.isConnected) {
      webSocket.sendMessage({ type: "refresh", channel: "metrics" })
    } else {
      // This part of the logic needs to be updated to fetch real metrics
      // For now, it will just return the current metrics if not connected
      // This might need to be changed based on how you want to handle this
      // when not connected to a real data source.
      // For now, it will just return the current metrics.
      // If you want to show a loading state or a default, you'd need to
      // manage a separate state for the "loading" or "default" metrics.
      // For now, it's just the current metrics.
    }
  }, [webSocket.isConnected, webSocket.sendMessage])

  return {
    metrics,
    connectionStatus,
    refreshMetrics,
    isRealTime: connectionStatus === "connected",
    error: webSocket.error,
  }
}
