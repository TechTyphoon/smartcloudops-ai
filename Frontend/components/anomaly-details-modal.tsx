"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { AlertTriangle, Clock, TrendingUp, Zap, CheckCircle, X } from "lucide-react"
import type { Anomaly } from "./anomaly-card"
import { cn } from "@/lib/utils"

interface AnomalyDetailsModalProps {
  anomaly: Anomaly | null
  isOpen: boolean
  onClose: () => void
  onAcknowledge: (id: string) => void
  onResolve: (id: string) => void
  onDismiss: (id: string) => void
}

const severityConfig = {
  critical: { color: "text-red-400", badge: "bg-red-500/20 text-red-300", icon: AlertTriangle },
  major: { color: "text-orange-400", badge: "bg-orange-500/20 text-orange-300", icon: AlertTriangle },
  minor: { color: "text-yellow-400", badge: "bg-yellow-500/20 text-yellow-300", icon: Clock },
  info: { color: "text-blue-400", badge: "bg-blue-500/20 text-blue-300", icon: Clock },
}

export function AnomalyDetailsModal({
  anomaly,
  isOpen,
  onClose,
  onAcknowledge,
  onResolve,
  onDismiss,
}: AnomalyDetailsModalProps) {
  if (!anomaly) return null

  const config = severityConfig[anomaly.severity]
  const Icon = config.icon

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <Icon className={cn("h-5 w-5", config.color)} />
            Anomaly Details - {anomaly.id}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Header Info */}
          <div className="flex items-center gap-4">
            <Badge className={config.badge}>{anomaly.severity.toUpperCase()}</Badge>
            <Badge variant="outline">{anomaly.service}</Badge>
            <div className="text-sm text-muted-foreground ml-auto">{new Date(anomaly.timestamp).toLocaleString()}</div>
          </div>

          {/* Description */}
          <div>
            <h3 className="font-semibold mb-2">Description</h3>
            <p className="text-sm text-muted-foreground">{anomaly.description}</p>
          </div>

          <Separator />

          {/* AI Analysis */}
          <div>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Zap className="h-4 w-4 text-teal-400" />
              AI Analysis
            </h3>

            {anomaly.aiConfidence && (
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>Confidence Score</span>
                  <span className="font-mono">{anomaly.aiConfidence}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-teal-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${anomaly.aiConfidence}%` }}
                  />
                </div>
              </div>
            )}

            {anomaly.rootCause && (
              <div className="bg-muted/50 rounded-lg p-4">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Root Cause Analysis
                </h4>
                <p className="text-sm text-muted-foreground">{anomaly.rootCause}</p>
              </div>
            )}
          </div>

          <Separator />

          {/* Timeline */}
          <div>
            <h3 className="font-semibold mb-3">Timeline</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full" />
                <span className="text-muted-foreground">{new Date(anomaly.timestamp).toLocaleString()}</span>
                <span>Anomaly detected</span>
              </div>
              {anomaly.status === "acknowledged" && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                  <span className="text-muted-foreground">{new Date().toLocaleString()}</span>
                  <span>Acknowledged by {anomaly.acknowledgedBy}</span>
                </div>
              )}
              {anomaly.resolvedAt && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span className="text-muted-foreground">{new Date(anomaly.resolvedAt).toLocaleString()}</span>
                  <span>Resolved</span>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          {anomaly.status === "active" && (
            <>
              <Separator />
              <div className="flex gap-3">
                <Button
                  onClick={() => {
                    onAcknowledge(anomaly.id)
                    onClose()
                  }}
                  className="flex-1"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Acknowledge
                </Button>
                <Button
                  onClick={() => {
                    onResolve(anomaly.id)
                    onClose()
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  Resolve
                </Button>
                <Button
                  onClick={() => {
                    onDismiss(anomaly.id)
                    onClose()
                  }}
                  variant="outline"
                  size="icon"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
