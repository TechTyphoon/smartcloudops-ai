"use client"

import { useEffect, useRef, useState, useCallback } from "react"

interface WebSocketConfig {
  url: string
  protocols?: string[]
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
  timeout?: number
}

interface WebSocketState {
  socket: WebSocket | null
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  reconnectAttempts: number
}

export function useWebSocket(config: WebSocketConfig) {
  const {
    url,
    protocols,
    reconnectInterval = 1000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    timeout = 10000,
  } = config

  const [state, setState] = useState<WebSocketState>({
    socket: null,
    isConnected: false,
    isConnecting: false,
    error: null,
    reconnectAttempts: 0,
  })

  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>()
  const connectionTimeoutRef = useRef<NodeJS.Timeout>()
  const messageHandlersRef = useRef<Set<(data: any) => void>>(new Set())

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
    }
    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current)
    }
  }, [])

  const connect = useCallback(() => {
    if (state.isConnecting || state.isConnected) return

    setState((prev) => ({ ...prev, isConnecting: true, error: null }))

    try {
      const socket = new WebSocket(url, protocols)

      connectionTimeoutRef.current = setTimeout(() => {
        if (socket.readyState === WebSocket.CONNECTING) {
          socket.close()
          setState((prev) => ({
            ...prev,
            isConnecting: false,
            error: "Connection timeout",
          }))
        }
      }, timeout)

      socket.onopen = () => {
        cleanup()
        setState((prev) => ({
          ...prev,
          socket,
          isConnected: true,
          isConnecting: false,
          error: null,
          reconnectAttempts: 0,
        }))

        heartbeatIntervalRef.current = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "ping" }))
          }
        }, heartbeatInterval)
      }

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type !== "pong") {
            messageHandlersRef.current.forEach((handler) => handler(data))
          }
        } catch (error) {
          console.warn("[WebSocket] Failed to parse message:", error)
        }
      }

      socket.onclose = (event) => {
        cleanup()
        setState((prev) => ({
          ...prev,
          socket: null,
          isConnected: false,
          isConnecting: false,
          error: event.wasClean ? null : "Connection lost",
        }))

        if (!event.wasClean && state.reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.min(reconnectInterval * Math.pow(2, state.reconnectAttempts), 30000)
          reconnectTimeoutRef.current = setTimeout(() => {
            setState((prev) => ({ ...prev, reconnectAttempts: prev.reconnectAttempts + 1 }))
            connect()
          }, delay)
        }
      }

      socket.onerror = () => {
        setState((prev) => ({
          ...prev,
          error: "WebSocket connection error",
          isConnecting: false,
        }))
      }
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isConnecting: false,
        error: error instanceof Error ? error.message : "Failed to create WebSocket",
      }))
    }
  }, [url, protocols, timeout, heartbeatInterval, maxReconnectAttempts, reconnectInterval, state.reconnectAttempts])

  const disconnect = useCallback(() => {
    cleanup()
    if (state.socket) {
      state.socket.close(1000, "Manual disconnect")
    }
    setState({
      socket: null,
      isConnected: false,
      isConnecting: false,
      error: null,
      reconnectAttempts: 0,
    })
  }, [state.socket, cleanup])

  const sendMessage = useCallback(
    (message: any) => {
      if (state.socket && state.isConnected) {
        try {
          state.socket.send(JSON.stringify(message))
          return true
        } catch (error) {
          console.error("[WebSocket] Failed to send message:", error)
          return false
        }
      }
      return false
    },
    [state.socket, state.isConnected],
  )

  const addMessageHandler = useCallback((handler: (data: any) => void) => {
    messageHandlersRef.current.add(handler)
    return () => messageHandlersRef.current.delete(handler)
  }, [])

  useEffect(() => {
    connect()
    return () => {
      cleanup()
      if (state.socket) {
        state.socket.close(1000, "Component unmount")
      }
    }
  }, [])

  return {
    isConnected: state.isConnected,
    isConnecting: state.isConnecting,
    error: state.error,
    reconnectAttempts: state.reconnectAttempts,
    connect,
    disconnect,
    sendMessage,
    addMessageHandler,
  }
}
