"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState, useMemo } from "react"
import { Search, FileText, User, Settings, Shield, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

export interface AuditLogEntry {
  id: string
  timestamp: string
  user: string
  action: string
  resource: string
  category: "authentication" | "configuration" | "remediation" | "monitoring" | "security"
  severity: "info" | "warning" | "critical"
  details: string
  ipAddress?: string
  userAgent?: string
}

interface AuditLogProps {
  entries: AuditLogEntry[]
}

const categoryConfig = {
  authentication: { icon: User, color: "text-blue-400", bg: "bg-blue-500/10" },
  configuration: { icon: Settings, color: "text-green-400", bg: "bg-green-500/10" },
  remediation: { icon: Shield, color: "text-purple-400", bg: "bg-purple-500/10" },
  monitoring: { icon: FileText, color: "text-teal-400", bg: "bg-teal-500/10" },
  security: { icon: AlertTriangle, color: "text-red-400", bg: "bg-red-500/10" },
}

const severityConfig = {
  info: { color: "text-blue-400", badge: "bg-blue-500/20 text-blue-300" },
  warning: { color: "text-yellow-400", badge: "bg-yellow-500/20 text-yellow-300" },
  critical: { color: "text-red-400", badge: "bg-red-500/20 text-red-300" },
}

export function AuditLog({ entries }: AuditLogProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [severityFilter, setSeverityFilter] = useState<string>("all")

  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      const matchesSearch =
        searchTerm === "" ||
        entry.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entry.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entry.resource.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesCategory = categoryFilter === "all" || entry.category === categoryFilter
      const matchesSeverity = severityFilter === "all" || entry.severity === severityFilter

      return matchesSearch && matchesCategory && matchesSeverity
    })
  }, [entries, searchTerm, categoryFilter, severityFilter])

  return (
    <Card className="bg-slate-950/50 border-slate-800">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2 text-teal-400">
          <FileText className="h-5 w-5" />
          Audit Log
        </CardTitle>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mt-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search audit logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-slate-900/50 border-slate-700"
              />
            </div>
          </div>

          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-full md:w-40 bg-slate-900/50 border-slate-700">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="authentication">Authentication</SelectItem>
              <SelectItem value="configuration">Configuration</SelectItem>
              <SelectItem value="remediation">Remediation</SelectItem>
              <SelectItem value="monitoring">Monitoring</SelectItem>
              <SelectItem value="security">Security</SelectItem>
            </SelectContent>
          </Select>

          <Select value={severityFilter} onValueChange={setSeverityFilter}>
            <SelectTrigger className="w-full md:w-40 bg-slate-900/50 border-slate-700">
              <SelectValue placeholder="Severity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Severities</SelectItem>
              <SelectItem value="info">Info</SelectItem>
              <SelectItem value="warning">Warning</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent>
        <ScrollArea className="h-96">
          <div className="space-y-3">
            {filteredEntries.map((entry) => {
              const categoryConf = categoryConfig[entry.category]
              const severityConf = severityConfig[entry.severity]
              const CategoryIcon = categoryConf.icon

              return (
                <div
                  key={entry.id}
                  className={cn(
                    "p-3 rounded-lg border border-slate-800 bg-slate-900/50",
                    "hover:bg-slate-800/50 transition-colors",
                    categoryConf.bg,
                  )}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <CategoryIcon className={cn("h-4 w-4", categoryConf.color)} />
                      <div>
                        <div className="font-medium text-sm">{entry.action}</div>
                        <div className="text-xs text-muted-foreground">{entry.resource}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className={cn("text-xs", severityConf.badge)}>
                        {entry.severity.toUpperCase()}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(entry.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>
                      User: <span className="text-foreground">{entry.user}</span>
                    </div>
                    {entry.ipAddress && (
                      <div>
                        IP: <span className="text-foreground font-mono">{entry.ipAddress}</span>
                      </div>
                    )}
                    <div className="mt-2 p-2 bg-slate-800/50 rounded text-xs">{entry.details}</div>
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
