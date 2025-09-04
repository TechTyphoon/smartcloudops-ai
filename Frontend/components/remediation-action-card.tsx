"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Play,
  Square,
  CheckCircle,
  XCircle,
  Clock,
  Shield,
  AlertTriangle,
  Zap,
  RefreshCw,
  Trash2,
  TrendingUp,
} from "lucide-react"
import { cn } from "@/lib/utils"

export interface RemediationAction {
  id: string
  name: string
  description: string
  category: "restart" | "scale" | "cleanup" | "config"
  severity: "low" | "medium" | "high" | "critical"
  requiresApproval: boolean
  canOverride: boolean
  lastExecuted?: string
  executionCount: number
  maxExecutionsPerHour: number
  status: "idle" | "pending-approval" | "running" | "success" | "failed" | "stopped"
  progress?: number
  estimatedDuration: string
  targetService: string
}

interface RemediationActionCardProps {
  action: RemediationAction
  onExecute: (id: string) => void
  onStop: (id: string) => void
  onApprove: (id: string) => void
  onOverride: (id: string) => void
}

const categoryConfig = {
  restart: { icon: RefreshCw, color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/20" },
  scale: { icon: TrendingUp, color: "text-green-400", bg: "bg-green-500/10 border-green-500/20" },
  cleanup: { icon: Trash2, color: "text-yellow-400", bg: "bg-yellow-500/10 border-yellow-500/20" },
  config: { icon: Zap, color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/20" },
}

const severityConfig = {
  low: { color: "text-green-400", badge: "bg-green-500/20 text-green-300" },
  medium: { color: "text-yellow-400", badge: "bg-yellow-500/20 text-yellow-300" },
  high: { color: "text-orange-400", badge: "bg-orange-500/20 text-orange-300" },
  critical: { color: "text-red-400", badge: "bg-red-500/20 text-red-300" },
}

export function RemediationActionCard({
  action,
  onExecute,
  onStop,
  onApprove,
  onOverride,
}: RemediationActionCardProps) {
  const [isProcessing, setIsProcessing] = useState(false)

  const categoryConf = categoryConfig[action.category]
  const severityConf = severityConfig[action.severity]
  const CategoryIcon = categoryConf.icon

  const isRateLimited = action.executionCount >= action.maxExecutionsPerHour
  const canExecute = !isRateLimited && action.status === "idle"
  const isRunning = action.status === "running"
  const needsApproval = action.status === "pending-approval"

  const handleAction = async (actionFn: () => void) => {
    setIsProcessing(true)
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, Math.random() * 1000 + 500))
    actionFn()
    setIsProcessing(false)
  }

  return (
    <Card
      className={cn(
        "border transition-all duration-300 hover:scale-[1.01]",
        categoryConf.bg,
        "bg-gradient-to-br from-background/50 to-background/80",
        isRunning && "ring-2 ring-teal-500/50 shadow-lg shadow-teal-500/20",
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={cn("p-2 rounded-lg border", categoryConf.bg, categoryConf.color)}>
              <CategoryIcon className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold">{action.name}</CardTitle>
              <p className="text-xs text-muted-foreground">{action.targetService}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={severityConf.badge} variant="outline">
              {action.severity.toUpperCase()}
            </Badge>
            {action.requiresApproval && (
              <Badge variant="outline" className="text-xs">
                <Shield className="h-3 w-3 mr-1" />
                APPROVAL
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{action.description}</p>

        {/* Execution Stats */}
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-muted-foreground">Executions Today:</span>
            <div className="font-mono font-semibold">
              {action.executionCount}/{action.maxExecutionsPerHour}
            </div>
          </div>
          <div>
            <span className="text-muted-foreground">Est. Duration:</span>
            <div className="font-mono font-semibold">{action.estimatedDuration}</div>
          </div>
        </div>

        {/* Rate Limiting Progress */}
        {action.executionCount > 0 && (
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span>Rate Limit</span>
              <span className={isRateLimited ? "text-red-400" : "text-muted-foreground"}>
                {action.executionCount}/{action.maxExecutionsPerHour}
              </span>
            </div>
            <Progress value={(action.executionCount / action.maxExecutionsPerHour) * 100} className="h-1" />
          </div>
        )}

        {/* Execution Progress */}
        {isRunning && action.progress !== undefined && (
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-teal-400">Executing...</span>
              <span className="font-mono">{action.progress}%</span>
            </div>
            <Progress value={action.progress} className="h-2" />
          </div>
        )}

        {/* Status Messages */}
        {action.status === "success" && (
          <div className="flex items-center gap-2 text-green-400 text-sm">
            <CheckCircle className="h-4 w-4" />
            Execution completed successfully
          </div>
        )}

        {action.status === "failed" && (
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <XCircle className="h-4 w-4" />
            Execution failed - check logs
          </div>
        )}

        {needsApproval && (
          <div className="flex items-center gap-2 text-yellow-400 text-sm">
            <Clock className="h-4 w-4" />
            Waiting for IT Manager approval
          </div>
        )}

        {isRateLimited && (
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <AlertTriangle className="h-4 w-4" />
            Rate limit exceeded - wait for reset
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          {canExecute && (
            <Button
              size="sm"
              onClick={() => handleAction(() => onExecute(action.id))}
              disabled={isProcessing}
              className="flex-1 bg-teal-600 hover:bg-teal-700"
            >
              <Play className="h-3 w-3 mr-1" />
              Execute
            </Button>
          )}

          {isRunning && (
            <Button
              size="sm"
              variant="destructive"
              onClick={() => handleAction(() => onStop(action.id))}
              disabled={isProcessing}
              className="flex-1"
            >
              <Square className="h-3 w-3 mr-1" />
              Stop
            </Button>
          )}

          {needsApproval && (
            <>
              <Button
                size="sm"
                onClick={() => handleAction(() => onApprove(action.id))}
                disabled={isProcessing}
                className="flex-1"
              >
                <CheckCircle className="h-3 w-3 mr-1" />
                Approve
              </Button>
              {action.canOverride && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleAction(() => onOverride(action.id))}
                  disabled={isProcessing}
                  className="border-orange-500/50 text-orange-400 hover:bg-orange-500/10"
                >
                  <Shield className="h-3 w-3 mr-1" />
                  Override
                </Button>
              )}
            </>
          )}
        </div>

        {action.lastExecuted && (
          <div className="text-xs text-muted-foreground">
            Last executed: {new Date(action.lastExecuted).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
