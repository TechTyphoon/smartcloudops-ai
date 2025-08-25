"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertTriangle, Clock, CheckCircle, X, Eye } from "lucide-react"
import { cn } from "@/lib/utils"

export interface Anomaly {
  id: string
  type: string
  severity: "critical" | "major" | "minor" | "info"
  timestamp: string
  service: string
  description: string
  rootCause?: string
  aiConfidence?: number
  status: "active" | "acknowledged" | "resolved" | "dismissed"
  acknowledgedBy?: string
  resolvedAt?: string
}

interface AnomalyCardProps {
  anomaly: Anomaly
  onAcknowledge: (id: string) => void
  onResolve: (id: string) => void
  onDismiss: (id: string) => void
  onViewDetails: (anomaly: Anomaly) => void
}

const severityConfig = {
  critical: {
    color: "bg-red-500/10 border-red-500/20 text-red-400",
    badge: "bg-red-500/20 text-red-300 border-red-500/30",
    glow: "shadow-red-500/20",
    icon: AlertTriangle,
  },
  major: {
    color: "bg-orange-500/10 border-orange-500/20 text-orange-400",
    badge: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    glow: "shadow-orange-500/20",
    icon: AlertTriangle,
  },
  minor: {
    color: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400",
    badge: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    glow: "shadow-yellow-500/20",
    icon: Clock,
  },
  info: {
    color: "bg-blue-500/10 border-blue-500/20 text-blue-400",
    badge: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    glow: "shadow-blue-500/20",
    icon: Clock,
  },
}

export function AnomalyCard({ anomaly, onAcknowledge, onResolve, onDismiss, onViewDetails }: AnomalyCardProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const config = severityConfig[anomaly.severity]
  const Icon = config.icon

  const handleAction = async (action: () => void) => {
    setIsProcessing(true)
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, Math.random() * 1000 + 500))
    action()
    setIsProcessing(false)
  }

  const isPulsingCritical = anomaly.severity === "critical" && anomaly.status === "active"

  return (
    <Card
      className={cn(
        "border transition-all duration-300 hover:scale-[1.02]",
        config.color,
        isPulsingCritical && "animate-pulse",
        anomaly.severity === "critical" && anomaly.status === "active" && `shadow-lg ${config.glow}`,
        anomaly.status !== "active" && "opacity-60",
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Icon className="h-5 w-5" />
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Badge variant="outline" className={cn("text-xs", config.badge)}>
                  {anomaly.severity.toUpperCase()}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {anomaly.id}
                </Badge>
              </div>
              <h3 className="font-semibold text-sm">{anomaly.type}</h3>
              <p className="text-xs text-muted-foreground">{anomaly.service}</p>
            </div>
          </div>
          <div className="text-xs text-muted-foreground">{new Date(anomaly.timestamp).toLocaleString()}</div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <p className="text-sm mb-4 text-muted-foreground">{anomaly.description}</p>

        {anomaly.aiConfidence && (
          <div className="mb-4">
            <div className="flex justify-between text-xs mb-1">
              <span>AI Confidence</span>
              <span>{anomaly.aiConfidence}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-1.5">
              <div
                className="bg-teal-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${anomaly.aiConfidence}%` }}
              />
            </div>
          </div>
        )}

        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={() => onViewDetails(anomaly)} className="flex-1">
            <Eye className="h-3 w-3 mr-1" />
            Details
          </Button>

          {anomaly.status === "active" && (
            <>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction(() => onAcknowledge(anomaly.id))}
                disabled={isProcessing}
                className="flex-1"
              >
                <CheckCircle className="h-3 w-3 mr-1" />
                Ack
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction(() => onResolve(anomaly.id))}
                disabled={isProcessing}
                className="flex-1"
              >
                Resolve
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction(() => onDismiss(anomaly.id))}
                disabled={isProcessing}
              >
                <X className="h-3 w-3" />
              </Button>
            </>
          )}
        </div>

        {anomaly.status !== "active" && (
          <div className="mt-2 text-xs text-muted-foreground">
            Status: {anomaly.status}
            {anomaly.acknowledgedBy && ` by ${anomaly.acknowledgedBy}`}
            {anomaly.resolvedAt && ` at ${new Date(anomaly.resolvedAt).toLocaleString()}`}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
