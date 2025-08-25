"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { DollarSign, TrendingDown, Lightbulb, Zap } from "lucide-react"
import { cn } from "@/lib/utils"

export interface CostOptimization {
  id: string
  title: string
  description: string
  potentialSavings: number
  currentCost: number
  category: "compute" | "storage" | "network" | "database"
  priority: "high" | "medium" | "low"
  aiConfidence: number
  implementationEffort: "low" | "medium" | "high"
  estimatedTimeToImplement: string
}

interface CostOptimizationCardProps {
  optimization: CostOptimization
  onImplement: (id: string) => void
}

const categoryConfig = {
  compute: { color: "text-blue-400", bg: "bg-blue-500/10" },
  storage: { color: "text-green-400", bg: "bg-green-500/10" },
  network: { color: "text-purple-400", bg: "bg-purple-500/10" },
  database: { color: "text-orange-400", bg: "bg-orange-500/10" },
}

const priorityConfig = {
  high: { color: "text-red-400", badge: "bg-red-500/20 text-red-300" },
  medium: { color: "text-yellow-400", badge: "bg-yellow-500/20 text-yellow-300" },
  low: { color: "text-green-400", badge: "bg-green-500/20 text-green-300" },
}

const effortConfig = {
  low: { color: "text-green-400", badge: "bg-green-500/20 text-green-300" },
  medium: { color: "text-yellow-400", badge: "bg-yellow-500/20 text-yellow-300" },
  high: { color: "text-red-400", badge: "bg-red-500/20 text-red-300" },
}

export function CostOptimizationCard({ optimization, onImplement }: CostOptimizationCardProps) {
  const categoryConf = categoryConfig[optimization.category]
  const priorityConf = priorityConfig[optimization.priority]
  const effortConf = effortConfig[optimization.implementationEffort]

  const savingsPercentage = (optimization.potentialSavings / optimization.currentCost) * 100

  return (
    <Card className={cn("border transition-all duration-300 hover:scale-[1.02]", categoryConf.bg, "border-slate-700")}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Lightbulb className={cn("h-4 w-4", categoryConf.color)} />
            <CardTitle className="text-sm font-semibold">{optimization.title}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={priorityConf.badge} variant="outline">
              {optimization.priority.toUpperCase()}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{optimization.description}</p>

        {/* Savings Info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-muted-foreground mb-1">Potential Savings</div>
            <div className="flex items-center gap-1">
              <DollarSign className="h-4 w-4 text-green-400" />
              <span className="font-bold text-green-400">${optimization.potentialSavings.toLocaleString()}</span>
            </div>
            <div className="text-xs text-muted-foreground">{savingsPercentage.toFixed(1)}% reduction</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground mb-1">Current Cost</div>
            <div className="font-mono text-sm">${optimization.currentCost.toLocaleString()}/month</div>
          </div>
        </div>

        {/* AI Confidence */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="flex items-center gap-1">
              <Zap className="h-3 w-3 text-teal-400" />
              AI Confidence
            </span>
            <span>{optimization.aiConfidence}%</span>
          </div>
          <Progress value={optimization.aiConfidence} className="h-1.5" />
        </div>

        {/* Implementation Details */}
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-muted-foreground">Effort:</span>
            <Badge className={cn("ml-2", effortConf.badge)} variant="outline">
              {optimization.implementationEffort.toUpperCase()}
            </Badge>
          </div>
          <div>
            <span className="text-muted-foreground">Time:</span>
            <span className="ml-2 font-mono">{optimization.estimatedTimeToImplement}</span>
          </div>
        </div>

        <Button onClick={() => onImplement(optimization.id)} className="w-full bg-teal-600 hover:bg-teal-700" size="sm">
          <TrendingDown className="h-3 w-3 mr-1" />
          Implement Optimization
        </Button>
      </CardContent>
    </Card>
  )
}
