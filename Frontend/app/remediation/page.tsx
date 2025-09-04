"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RemediationActionCard, type RemediationAction } from "@/components/remediation-action-card"
import { ActionLog, type ActionLogEntry } from "@/components/action-log"
import { Search, Terminal, Shield, Zap, AlertTriangle } from "lucide-react"
import { apiService } from "@/lib/api"

export default function RemediationPage() {
  const [actions, setActions] = useState<RemediationAction[]>([])
  const [logEntries, setLogEntries] = useState<ActionLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [emergencyStop, setEmergencyStop] = useState(false)

  const filteredActions = actions.filter((action) => {
    const matchesSearch =
      searchTerm === "" ||
      action.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      action.targetService.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesCategory = categoryFilter === "all" || action.category === categoryFilter

    return matchesSearch && matchesCategory
  })

  const handleExecute = (id: string) => {
    setActions((prev) =>
      prev.map((action) =>
        action.id === id
          ? { ...action, status: action.requiresApproval ? "pending-approval" : "running", progress: 0 }
          : action,
      ),
    )

    // Simulate execution
    if (!actions.find((a) => a.id === id)?.requiresApproval) {
      setTimeout(() => {
        setActions((prev) =>
          prev.map((action) =>
            action.id === id
              ? { ...action, status: "success", progress: 100, executionCount: action.executionCount + 1 }
              : action,
          ),
        )

        // Add to log
        const action = actions.find((a) => a.id === id)
        if (action) {
          setLogEntries((prev) => [
            {
              id: `LOG-${Date.now()}`,
              actionName: action.name,
              targetService: action.targetService,
              status: "success",
              timestamp: new Date().toISOString(),
              duration: "1m 23s",
              executedBy: "current.user@company.com",
              details: "Action completed successfully.",
            },
            ...prev,
          ])
        }
      }, 3000)
    }
  }

  const handleStop = async (id: string) => {
    try {
      await apiService.stopRemediationAction(id)
      // Refresh actions after stop
      const actionsData = await apiService.getRemediationActions()
      setActions(actionsData)
    } catch (err) {
      console.error('Failed to stop remediation action:', err)
    }
  }

  const handleApprove = async (id: string) => {
    try {
      await apiService.approveRemediationAction(id)
      // Refresh actions after approval
      const actionsData = await apiService.getRemediationActions()
      setActions(actionsData)
    } catch (err) {
      console.error('Failed to approve remediation action:', err)
    }
  }

  const handleOverride = async (id: string) => {
    try {
      await apiService.overrideRemediationAction(id)
      // Refresh actions after override
      const actionsData = await apiService.getRemediationActions()
      setActions(actionsData)
    } catch (err) {
      console.error('Failed to override remediation action:', err)
    }
  }

  const handleEmergencyStop = async () => {
    try {
      await apiService.emergencyStop()
      setEmergencyStop(true)
      setTimeout(() => setEmergencyStop(false), 3000)
    } catch (err) {
      console.error('Failed to trigger emergency stop:', err)
    }
  }

  const runningActions = actions.filter((a) => a.status === "running").length
  const pendingApprovals = actions.filter((a) => a.status === "pending-approval").length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Terminal className="h-8 w-8 text-teal-400" />
            Remediation Control Center
          </h1>
          <p className="text-muted-foreground">Autonomous CloudOps command center for system remediation</p>
        </div>

        <Button
          variant="destructive"
          onClick={handleEmergencyStop}
          disabled={emergencyStop || runningActions === 0}
          className="bg-red-600 hover:bg-red-700"
        >
          <AlertTriangle className="h-4 w-4 mr-2" />
          {emergencyStop ? "STOPPING..." : "EMERGENCY STOP"}
        </Button>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-teal-500/20 bg-teal-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-teal-400 flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Active Executions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-teal-400">{runningActions}</div>
          </CardContent>
        </Card>

        <Card className="border-yellow-500/20 bg-yellow-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-yellow-400 flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Pending Approvals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{pendingApprovals}</div>
          </CardContent>
        </Card>

        <Card className="border-blue-500/20 bg-blue-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-blue-400 flex items-center gap-2">
              <Terminal className="h-4 w-4" />
              Available Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">{actions.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-slate-950/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg text-teal-400">Command Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search actions or services..."
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
                <SelectItem value="restart">Restart</SelectItem>
                <SelectItem value="scale">Scale</SelectItem>
                <SelectItem value="cleanup">Cleanup</SelectItem>
                <SelectItem value="config">Config</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Actions Grid */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-teal-400">Available Actions</h2>
          <div className="space-y-4">
            {filteredActions.map((action) => (
              <RemediationActionCard
                key={action.id}
                action={action}
                onExecute={handleExecute}
                onStop={handleStop}
                onApprove={handleApprove}
                onOverride={handleOverride}
              />
            ))}
          </div>
        </div>

        {/* Action Log */}
        <div>
          <ActionLog entries={logEntries} />
        </div>
      </div>
    </div>
  )
}
