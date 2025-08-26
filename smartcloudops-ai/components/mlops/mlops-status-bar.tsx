"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { 
  Activity, 
  Clock, 
  Wifi, 
  WifiOff,
  Settings,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from "lucide-react"
import { useMLOpsRealTime, REALTIME_PRESETS, type RealtimePreset } from "@/hooks/use-mlops-real-time"
import { useMLOpsStore } from "@/lib/stores/mlops-store"

interface MLOpsStatusBarProps {
  className?: string
}

export function MLOpsStatusBar({ className }: MLOpsStatusBarProps) {
  const {
    enabled,
    interval,
    connectionStatus,
    lastRefresh,
    start,
    stop,
    setInterval,
    currentCounts,
    isConnected,
    isReconnecting
  } = useMLOpsRealTime({
    enableNotifications: true,
    notificationThreshold: { experiments: 1, models: 1, dataVersions: 1 }
  })

  const { refreshing, clearErrors } = useMLOpsStore()
  const [showSettings, setShowSettings] = useState(false)

  // Format time since last refresh
  const getLastRefreshText = () => {
    if (!lastRefresh) return 'Never'
    const secondsAgo = Math.floor((Date.now() - lastRefresh.getTime()) / 1000)
    
    if (secondsAgo < 60) return `${secondsAgo}s ago`
    if (secondsAgo < 3600) return `${Math.floor(secondsAgo / 60)}m ago`
    return `${Math.floor(secondsAgo / 3600)}h ago`
  }

  // Status indicator
  const getStatusIndicator = () => {
    if (refreshing) {
      return (
        <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20">
          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
          Updating
        </Badge>
      )
    }

    if (!enabled) {
      return (
        <Badge variant="outline" className="bg-gray-500/10 text-gray-500 border-gray-500/20">
          <WifiOff className="w-3 h-3 mr-1" />
          Offline
        </Badge>
      )
    }

    if (isReconnecting) {
      return (
        <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">
          <AlertCircle className="w-3 h-3 mr-1" />
          Reconnecting
        </Badge>
      )
    }

    if (isConnected) {
      return (
        <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">
          <Activity className="w-3 h-3 mr-1 animate-pulse" />
          Live
        </Badge>
      )
    }

    return (
      <Badge variant="outline" className="bg-gray-500/10 text-gray-500 border-gray-500/20">
        <Wifi className="w-3 h-3 mr-1" />
        Connected
      </Badge>
    )
  }

  const handlePresetChange = (preset: RealtimePreset) => {
    const config = REALTIME_PRESETS[preset]
    setInterval(config.interval)
  }

  const formatInterval = (ms: number) => {
    return `${ms / 1000}s`
  }

  return (
    <Card className={className}>
      <CardContent className="p-3">
        <div className="flex items-center justify-between">
          {/* Left side - Status and Stats */}
          <div className="flex items-center gap-3">
            {getStatusIndicator()}
            
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Clock className="w-3 h-3" />
              {getLastRefreshText()}
            </div>
            
            <Separator orientation="vertical" className="h-4" />
            
            <div className="flex items-center gap-3 text-sm">
              <span className="text-muted-foreground">
                <span className="font-medium text-foreground">{currentCounts.experiments}</span> experiments
              </span>
              <span className="text-muted-foreground">
                <span className="font-medium text-foreground">{currentCounts.models}</span> models
              </span>
              <span className="text-muted-foreground">
                <span className="font-medium text-foreground">{currentCounts.dataVersions}</span> data versions
              </span>
            </div>
          </div>

          {/* Right side - Controls */}
          <div className="flex items-center gap-2">
            {showSettings && (
              <div className="flex items-center gap-2 mr-2">
                <Select 
                  value={interval.toString()} 
                  onValueChange={(value) => setInterval(parseInt(value))}
                >
                  <SelectTrigger className="w-24 h-7 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5000">5s</SelectItem>
                    <SelectItem value="10000">10s</SelectItem>
                    <SelectItem value="30000">30s</SelectItem>
                    <SelectItem value="60000">1m</SelectItem>
                    <SelectItem value="300000">5m</SelectItem>
                  </SelectContent>
                </Select>

                <Select onValueChange={handlePresetChange}>
                  <SelectTrigger className="w-20 h-7 text-xs">
                    <SelectValue placeholder="Preset" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="development">Dev</SelectItem>
                    <SelectItem value="production">Prod</SelectItem>
                    <SelectItem value="demo">Demo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
              className="h-7 px-2"
            >
              <Settings className="w-3 h-3" />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={enabled ? stop : start}
              className="h-7 px-2"
            >
              {enabled ? <WifiOff className="w-3 h-3" /> : <Wifi className="w-3 h-3" />}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
