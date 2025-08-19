"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertTriangle, Clock, CheckCircle, X, Eye, Loader2 } from "lucide-react"
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
    color: "bg-destructive/10 border-destructive/20 text-destructive",
    badge: "bg-destructive/20 text-destructive border-destructive/30",
    glow: "shadow-destructive/20",
    icon: AlertTriangle,
    label: "Critical",
    description: "Requires immediate attention"
  },
  major: {
    color: "bg-orange-500/10 border-orange-500/20 text-orange-600 dark:text-orange-400",
    badge: "bg-orange-500/20 text-orange-600 dark:text-orange-400 border-orange-500/30",
    glow: "shadow-orange-500/20",
    icon: AlertTriangle,
    label: "Major",
    description: "High priority issue"
  },
  minor: {
    color: "bg-amber-500/10 border-amber-500/20 text-amber-600 dark:text-amber-400",
    badge: "bg-amber-500/20 text-amber-600 dark:text-amber-400 border-amber-500/30",
    glow: "shadow-amber-500/20",
    icon: Clock,
    label: "Minor",
    description: "Low priority issue"
  },
  info: {
    color: "bg-blue-500/10 border-blue-500/20 text-blue-600 dark:text-blue-400",
    badge: "bg-blue-500/20 text-blue-600 dark:text-blue-400 border-blue-500/30",
    glow: "shadow-blue-500/20",
    icon: Clock,
    label: "Info",
    description: "Informational message"
  },
}

export function AnomalyCard({ anomaly, onAcknowledge, onResolve, onDismiss, onViewDetails }: AnomalyCardProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const config = severityConfig[anomaly.severity]
  const Icon = config.icon

  const handleAction = useCallback(async (action: () => void) => {
    setIsProcessing(true)
    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, Math.random() * 1000 + 500))
      action()
    } catch (error) {
      console.error('Action failed:', error)
    } finally {
      setIsProcessing(false)
    }
  }, [])

  const isPulsingCritical = anomaly.severity === "critical" && anomaly.status === "active"
  const isActive = anomaly.status === "active"

  const formatTimestamp = useCallback((timestamp: string) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(new Date(timestamp))
  }, [])

  return (
    <Card
      className={cn(
        "border transition-all duration-300 hover:scale-[1.02] focus-within:scale-[1.02] focus-within:ring-2 focus-within:ring-ring",
        config.color,
        isPulsingCritical && "animate-pulse",
        anomaly.severity === "critical" && anomaly.status === "active" && `shadow-lg ${config.glow}`,
        anomaly.status !== "active" && "opacity-60",
        "group"
      )}
      role="article"
      aria-labelledby={`anomaly-${anomaly.id}-title`}
      aria-describedby={`anomaly-${anomaly.id}-description`}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0 flex-1">
            <Icon 
              className="h-5 w-5 shrink-0 mt-0.5" 
              aria-hidden="true"
            />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <Badge 
                  variant="outline" 
                  className={cn("text-xs font-medium", config.badge)}
                  aria-label={`Severity: ${config.label}`}
                >
                  {config.label}
                </Badge>
                <Badge 
                  variant="outline" 
                  className="text-xs bg-muted/50"
                  aria-label={`Anomaly ID: ${anomaly.id}`}
                >
                  {anomaly.id}
                </Badge>
              </div>
              <h3 
                id={`anomaly-${anomaly.id}-title`}
                className="font-semibold text-sm mb-1 truncate"
              >
                {anomaly.type}
              </h3>
              <p className="text-xs text-muted-foreground truncate">
                {anomaly.service}
              </p>
            </div>
          </div>
          <time 
            className="text-xs text-muted-foreground shrink-0"
            dateTime={anomaly.timestamp}
            aria-label={`Detected at ${formatTimestamp(anomaly.timestamp)}`}
          >
            {formatTimestamp(anomaly.timestamp)}
          </time>
        </div>
      </CardHeader>

      <CardContent className="pt-0 space-y-4">
        <p 
          id={`anomaly-${anomaly.id}-description`}
          className="text-sm text-muted-foreground leading-relaxed"
        >
          {anomaly.description}
        </p>

        {anomaly.aiConfidence && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>AI Confidence</span>
              <span className="font-medium">{anomaly.aiConfidence}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${anomaly.aiConfidence}%` }}
                role="progressbar"
                aria-valuenow={anomaly.aiConfidence}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`AI confidence level: ${anomaly.aiConfidence}%`}
              />
            </div>
          </div>
        )}

        <div className="flex items-center gap-2 flex-wrap">
          <Button 
            size="sm" 
            variant="outline" 
            onClick={() => onViewDetails(anomaly)} 
            className="flex-1 min-w-0 enterprise-focus"
            aria-label={`View details for ${anomaly.type}`}
          >
            <Eye className="h-3 w-3 mr-1 shrink-0" />
            <span className="truncate">Details</span>
          </Button>

          {isActive && (
            <>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction(() => onAcknowledge(anomaly.id))}
                disabled={isProcessing}
                className="flex-1 min-w-0 enterprise-focus"
                aria-label={`Acknowledge ${anomaly.type}`}
              >
                {isProcessing ? (
                  <Loader2 className="h-3 w-3 mr-1 animate-spin shrink-0" />
                ) : (
                  <CheckCircle className="h-3 w-3 mr-1 shrink-0" />
                )}
                <span className="truncate">Ack</span>
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction(() => onResolve(anomaly.id))}
                disabled={isProcessing}
                className="flex-1 min-w-0 enterprise-focus"
                aria-label={`Resolve ${anomaly.type}`}
              >
                {isProcessing ? (
                  <Loader2 className="h-3 w-3 mr-1 animate-spin shrink-0" />
                ) : (
                  <span className="truncate">Resolve</span>
                )}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleAction(() => onDismiss(anomaly.id))}
                disabled={isProcessing}
                className="shrink-0 enterprise-focus"
                aria-label={`Dismiss ${anomaly.type}`}
              >
                {isProcessing ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <X className="h-3 w-3" />
                )}
              </Button>
            </>
          )}
        </div>

        {anomaly.status !== "active" && (
          <div className="mt-3 p-2 bg-muted/50 rounded-lg">
            <p className="text-xs text-muted-foreground">
              <span className="font-medium capitalize">{anomaly.status}</span>
              {anomaly.acknowledgedBy && (
                <span> by {anomaly.acknowledgedBy}</span>
              )}
              {anomaly.resolvedAt && (
                <span> at {formatTimestamp(anomaly.resolvedAt)}</span>
              )}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
