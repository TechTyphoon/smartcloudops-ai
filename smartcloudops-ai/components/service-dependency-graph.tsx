"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Network, Database, Globe, Server, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

export interface ServiceNode {
  id: string
  name: string
  type: "api" | "database" | "cache" | "external"
  status: "healthy" | "warning" | "critical"
  dependencies: string[]
}

interface ServiceDependencyGraphProps {
  services: ServiceNode[]
}

const typeConfig = {
  api: { icon: Server, color: "text-blue-400", bg: "bg-blue-500/10" },
  database: { icon: Database, color: "text-green-400", bg: "bg-green-500/10" },
  cache: { icon: Network, color: "text-purple-400", bg: "bg-purple-500/10" },
  external: { icon: Globe, color: "text-orange-400", bg: "bg-orange-500/10" },
}

const statusConfig = {
  healthy: { color: "border-green-500", bg: "bg-green-500/5" },
  warning: { color: "border-yellow-500", bg: "bg-yellow-500/5" },
  critical: { color: "border-red-500", bg: "bg-red-500/5" },
}

export function ServiceDependencyGraph({ services }: ServiceDependencyGraphProps) {
  return (
    <Card className="bg-slate-950/50 border-slate-800">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2 text-teal-400">
          <Network className="h-5 w-5" />
          Service Dependencies
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {services.map((service) => {
            const typeConf = typeConfig[service.type]
            const statusConf = statusConfig[service.status]
            const TypeIcon = typeConf.icon

            return (
              <div key={service.id} className="space-y-2">
                <div
                  className={cn(
                    "p-3 rounded-lg border-2 transition-all duration-300",
                    statusConf.color,
                    statusConf.bg,
                    typeConf.bg,
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <TypeIcon className={cn("h-5 w-5", typeConf.color)} />
                      <div>
                        <div className="font-semibold text-sm">{service.name}</div>
                        <div className="text-xs text-muted-foreground capitalize">{service.type}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {service.status === "critical" && <AlertTriangle className="h-4 w-4 text-red-400" />}
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-xs",
                          service.status === "healthy" && "text-green-400 border-green-500/50",
                          service.status === "warning" && "text-yellow-400 border-yellow-500/50",
                          service.status === "critical" && "text-red-400 border-red-500/50",
                        )}
                      >
                        {service.status.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  {service.dependencies.length > 0 && (
                    <div>
                      <div className="text-xs text-muted-foreground mb-2">Dependencies:</div>
                      <div className="flex flex-wrap gap-1">
                        {service.dependencies.map((dep) => {
                          const depService = services.find((s) => s.id === dep)
                          return (
                            <Badge
                              key={dep}
                              variant="outline"
                              className={cn(
                                "text-xs",
                                depService?.status === "healthy" && "border-green-500/30 text-green-400",
                                depService?.status === "warning" && "border-yellow-500/30 text-yellow-400",
                                depService?.status === "critical" && "border-red-500/30 text-red-400",
                              )}
                            >
                              {depService?.name || dep}
                            </Badge>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
