"use client"

import { Badge } from "@/components/ui/badge"
import { Wifi, WifiOff, RefreshCw, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

interface RealTimeStatusProps {
  status: "connected" | "connecting" | "disconnected" | "fallback"
  error?: string | null
  className?: string
}

export function RealTimeStatus({ status, error, className }: RealTimeStatusProps) {
  const getStatusConfig = () => {
    switch (status) {
      case "connected":
        return {
          icon: Wifi,
          text: "Live",
          variant: "default" as const,
          className: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30 realtime-active",
        }
      case "connecting":
        return {
          icon: RefreshCw,
          text: "Connecting",
          variant: "secondary" as const,
          className: "bg-blue-500/20 text-blue-400 border-blue-500/30",
          animate: true,
        }
      case "fallback":
        return {
          icon: RefreshCw,
          text: "Polling",
          variant: "outline" as const,
          className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        }
      case "disconnected":
      default:
        return {
          icon: error ? AlertTriangle : WifiOff,
          text: error ? "Error" : "Offline",
          variant: "destructive" as const,
          className: "bg-red-500/20 text-red-400 border-red-500/30",
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <Badge variant={config.variant} className={cn("flex items-center gap-1.5 text-xs", config.className, className)}>
      <Icon className={cn("h-3 w-3", config.animate && "animate-spin")} />
      <span>{config.text}</span>
    </Badge>
  )
}
