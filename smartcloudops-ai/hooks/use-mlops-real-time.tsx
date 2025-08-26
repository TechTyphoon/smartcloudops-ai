/**
 * Custom hook for MLOps real-time functionality
 * Phase 2B Week 2: State Management & UX - Real-time Updates
 */

import { useEffect, useCallback } from 'react'
import { useRealTime, useMLOpsStore } from '@/lib/stores/mlops-store'
import { toast } from 'sonner'

interface UseMLOpsRealTimeOptions {
  enableNotifications?: boolean
  notificationThreshold?: {
    experiments?: number
    models?: number
    dataVersions?: number
  }
  onDataUpdate?: (type: 'experiments' | 'models' | 'data' | 'stats') => void
}

export function useMLOpsRealTime(options: UseMLOpsRealTimeOptions = {}) {
  const { 
    enabled, 
    interval, 
    start, 
    stop, 
    setInterval: setUpdateInterval 
  } = useRealTime()
  
  const { 
    experiments, 
    models, 
    dataVersions, 
    statistics,
    lastRefresh 
  } = useMLOpsStore()

  const {
    enableNotifications = false,
    notificationThreshold = {},
    onDataUpdate
  } = options

  // Track previous counts for notifications
  const previousCounts = useMLOpsStore(state => ({
    experiments: state.experiments.length,
    models: state.models.length,
    dataVersions: state.dataVersions.length
  }))

  // Notification handler
  const handleDataChange = useCallback((type: 'experiments' | 'models' | 'data' | 'stats') => {
    if (enableNotifications) {
      const currentCounts = {
        experiments: experiments.length,
        models: models.length,
        dataVersions: dataVersions.length
      }

      // Check for new items and show notifications
      if (type === 'experiments' && currentCounts.experiments > previousCounts.experiments) {
        const newCount = currentCounts.experiments - previousCounts.experiments
        if (newCount >= (notificationThreshold.experiments || 1)) {
          toast.success(`${newCount} new experiment(s) created`)
        }
      }

      if (type === 'models' && currentCounts.models > previousCounts.models) {
        const newCount = currentCounts.models - previousCounts.models
        if (newCount >= (notificationThreshold.models || 1)) {
          toast.success(`${newCount} new model(s) registered`)
        }
      }

      if (type === 'data' && currentCounts.dataVersions > previousCounts.dataVersions) {
        const newCount = currentCounts.dataVersions - previousCounts.dataVersions
        if (newCount >= (notificationThreshold.dataVersions || 1)) {
          toast.success(`${newCount} new data version(s) available`)
        }
      }
    }

    // Call custom handler
    onDataUpdate?.(type)
  }, [
    enableNotifications, 
    notificationThreshold, 
    onDataUpdate, 
    experiments.length, 
    models.length, 
    dataVersions.length,
    previousCounts
  ])

  // Monitor data changes
  useEffect(() => {
    if (enabled && lastRefresh) {
      handleDataChange('experiments')
    }
  }, [experiments.length, enabled, lastRefresh, handleDataChange])

  useEffect(() => {
    if (enabled && lastRefresh) {
      handleDataChange('models')
    }
  }, [models.length, enabled, lastRefresh, handleDataChange])

  useEffect(() => {
    if (enabled && lastRefresh) {
      handleDataChange('data')
    }
  }, [dataVersions.length, enabled, lastRefresh, handleDataChange])

  useEffect(() => {
    if (enabled && lastRefresh) {
      handleDataChange('stats')
    }
  }, [statistics, enabled, lastRefresh, handleDataChange])

  // Connection status
  const getConnectionStatus = useCallback(() => {
    if (!enabled) return 'disconnected'
    if (lastRefresh && Date.now() - lastRefresh.getTime() < interval * 1.5) {
      return 'connected'
    }
    return 'reconnecting'
  }, [enabled, lastRefresh, interval])

  // Control functions
  const startRealTime = useCallback(() => {
    start()
    if (enableNotifications) {
      toast.success('Real-time updates enabled')
    }
  }, [start, enableNotifications])

  const stopRealTime = useCallback(() => {
    stop()
    if (enableNotifications) {
      toast.info('Real-time updates disabled')
    }
  }, [stop, enableNotifications])

  const updateInterval = useCallback((newInterval: number) => {
    setUpdateInterval(newInterval)
    if (enableNotifications) {
      toast.info(`Update interval changed to ${newInterval / 1000}s`)
    }
  }, [setUpdateInterval, enableNotifications])

  return {
    // Status
    enabled,
    interval,
    connectionStatus: getConnectionStatus(),
    lastRefresh,
    
    // Controls
    start: startRealTime,
    stop: stopRealTime,
    setInterval: updateInterval,
    
    // Data
    currentCounts: {
      experiments: experiments.length,
      models: models.length,
      dataVersions: dataVersions.length
    },
    
    // Utilities
    isConnected: getConnectionStatus() === 'connected',
    isReconnecting: getConnectionStatus() === 'reconnecting'
  }
}

// Preset configurations
export const REALTIME_PRESETS = {
  development: {
    interval: 10000, // 10 seconds
    enableNotifications: true,
    notificationThreshold: { experiments: 1, models: 1, dataVersions: 1 }
  },
  production: {
    interval: 30000, // 30 seconds
    enableNotifications: false,
    notificationThreshold: { experiments: 5, models: 3, dataVersions: 10 }
  },
  demo: {
    interval: 5000, // 5 seconds
    enableNotifications: true,
    notificationThreshold: { experiments: 1, models: 1, dataVersions: 1 }
  }
} as const

export type RealtimePreset = keyof typeof REALTIME_PRESETS
