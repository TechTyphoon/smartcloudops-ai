"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CheckCircle, XCircle, Clock, Play, Square, Shield } from "lucide-react"
import { cn } from "@/lib/utils"

export interface ActionLogEntry {
  id: string
  actionName: string
  targetService: string
  status: "success" | "failed" | "running" | "stopped" | "approved" | "overridden"
  timestamp: string
  duration?: string
  executedBy: string
  details?: string
  approvedBy?: string
}

interface ActionLogProps {
  entries: ActionLogEntry[]
}

const statusConfig = {
  success: { icon: CheckCircle, color: "text-green-400", bg: "bg-green-500/10" },
  failed: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10" },
  running: { icon: Play, color: "text-blue-400", bg: "bg-blue-500/10" },
  stopped: { icon: Square, color: "text-orange-400", bg: "bg-orange-500/10" },
  approved: { icon: CheckCircle, color: "text-teal-400", bg: "bg-teal-500/10" },
  overridden: { icon: Shield, color: "text-purple-400", bg: "bg-purple-500/10" },
}

export function ActionLog({ entries }: ActionLogProps) {
  return (
    <Card className="bg-slate-950/50 border-slate-800">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2 text-teal-400">
          <Clock className="h-5 w-5" />
          Action Log
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-96">
          <div className="space-y-3">
            {entries.map((entry) => {
              const config = statusConfig[entry.status]
              const StatusIcon = config.icon

              return (
                <div
                  key={entry.id}
                  className={cn(
                    "p-3 rounded-lg border border-slate-800 bg-slate-900/50",
                    "hover:bg-slate-800/50 transition-colors",
                  )}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={cn("p-1.5 rounded", config.bg)}>
                        <StatusIcon className={cn("h-3 w-3", config.color)} />
                      </div>
                      <div>
                        <div className="font-medium text-sm">{entry.actionName}</div>
                        <div className="text-xs text-muted-foreground">{entry.targetService}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className={cn("text-xs", config.color)}>
                        {entry.status.toUpperCase()}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(entry.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>
                      Executed by: <span className="text-foreground">{entry.executedBy}</span>
                    </div>
                    {entry.duration && (
                      <div>
                        Duration: <span className="text-foreground font-mono">{entry.duration}</span>
                      </div>
                    )}
                    {entry.approvedBy && (
                      <div>
                        Approved by: <span className="text-foreground">{entry.approvedBy}</span>
                      </div>
                    )}
                    {entry.details && <div className="mt-2 p-2 bg-slate-800/50 rounded text-xs">{entry.details}</div>}
                  </div>
                </div>
              )
            })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
