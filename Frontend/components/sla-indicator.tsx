"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Minus, Target } from "lucide-react"
import { cn } from "@/lib/utils"

export interface SLAMetric {
  id: string
  name: string
  current: number
  target: number
  trend: "up" | "down" | "stable"
  status: "healthy" | "warning" | "critical"
  period: string
  description: string
}

interface SLAIndicatorProps {
  metric: SLAMetric
}

const statusConfig = {
  healthy: {
    color: "text-green-400",
    bg: "bg-green-500/10 border-green-500/20",
    badge: "bg-green-500/20 text-green-300",
  },
  warning: {
    color: "text-yellow-400",
    bg: "bg-yellow-500/10 border-yellow-500/20",
    badge: "bg-yellow-500/20 text-yellow-300",
  },
  critical: { color: "text-red-400", bg: "bg-red-500/10 border-red-500/20", badge: "bg-red-500/20 text-red-300" },
}

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
}

export function SLAIndicator({ metric }: SLAIndicatorProps) {
  const config = statusConfig[metric.status]
  const TrendIcon = trendIcons[metric.trend]
  const percentage = (metric.current / metric.target) * 100

  return (
    <Card className={cn("border transition-all duration-300 hover:scale-[1.02]", config.bg)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Target className="h-4 w-4" />
            {metric.name}
          </CardTitle>
          <Badge className={config.badge} variant="outline">
            {metric.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold font-mono">{metric.current.toFixed(2)}%</div>
            <div className="text-xs text-muted-foreground">Target: {metric.target}%</div>
          </div>
          <div className={cn("flex items-center gap-1", config.color)}>
            <TrendIcon className="h-4 w-4" />
            <span className="text-sm font-medium">{metric.trend}</span>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span>Progress to Target</span>
            <span>{percentage.toFixed(1)}%</span>
          </div>
          <Progress
            value={Math.min(percentage, 100)}
            className={cn("h-2", percentage >= 100 ? "bg-green-500/20" : "bg-muted")}
          />
        </div>

        <div className="text-xs text-muted-foreground">
          <div className="mb-1">{metric.description}</div>
          <div>Period: {metric.period}</div>
        </div>
      </CardContent>
    </Card>
  )
}
