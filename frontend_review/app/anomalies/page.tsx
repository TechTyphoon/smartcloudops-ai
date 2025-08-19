"use client"

import { useState, useMemo, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AnomalyCard, type Anomaly } from "@/components/anomaly-card"
import { AnomalyDetailsModal } from "@/components/anomaly-details-modal"
import { Search, Filter, AlertTriangle, Clock, CheckCircle, Loader2 } from "lucide-react"
import { apiClient } from "@/lib/api"

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [severityFilter, setSeverityFilter] = useState<string>("all")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch real anomalies from backend
  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const response = await apiClient.getAnomalies()
        
        if (response.status === 'success' && response.data) {
          // Transform backend data to frontend format
          const realAnomalies: Anomaly[] = Array.isArray(response.data) 
            ? response.data.map((anomaly: any) => ({
                id: anomaly.id || `ANO-${Date.now()}`,
                type: anomaly.type || anomaly.name || 'Unknown Anomaly',
                severity: anomaly.severity || 'info',
                timestamp: anomaly.timestamp || new Date().toISOString(),
                service: anomaly.service || anomaly.target || 'unknown',
                description: anomaly.description || anomaly.message || 'No description available',
                rootCause: anomaly.root_cause || anomaly.cause || 'Root cause analysis pending',
                aiConfidence: anomaly.ai_confidence || anomaly.confidence || 0,
                status: anomaly.status || 'active',
                acknowledgedBy: anomaly.acknowledged_by,
                resolvedAt: anomaly.resolved_at,
              }))
            : []

          setAnomalies(realAnomalies)
        } else {
          setError('Failed to fetch anomalies')
        }
      } catch (err) {
        setError('Error connecting to backend')
        console.error('Failed to fetch anomalies:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAnomalies()

    // Set up polling for real-time updates
    const interval = setInterval(fetchAnomalies, 60000) // Poll every minute

    return () => clearInterval(interval)
  }, [])

  const filteredAnomalies = useMemo(() => {
    return anomalies.filter((anomaly) => {
      const matchesSearch =
        searchTerm === "" ||
        anomaly.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        anomaly.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
        anomaly.id.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesSeverity = severityFilter === "all" || anomaly.severity === severityFilter
      const matchesStatus = statusFilter === "all" || anomaly.status === statusFilter

      return matchesSearch && matchesSeverity && matchesStatus
    })
  }, [anomalies, searchTerm, severityFilter, statusFilter])

  const handleAcknowledge = async (id: string) => {
    try {
      const response = await apiClient.acknowledgeAnomaly(id)
      if (response.status === 'success') {
        setAnomalies((prev) =>
          prev.map((anomaly) =>
            anomaly.id === id
              ? { ...anomaly, status: "acknowledged" as const, acknowledgedBy: "current.user@company.com" }
              : anomaly,
          ),
        )
      }
    } catch (error) {
      console.error('Failed to acknowledge anomaly:', error)
    }
  }

  const handleResolve = async (id: string) => {
    try {
      const response = await apiClient.resolveAnomaly(id)
      if (response.status === 'success') {
        setAnomalies((prev) =>
          prev.map((anomaly) =>
            anomaly.id === id ? { ...anomaly, status: "resolved" as const, resolvedAt: new Date().toISOString() } : anomaly,
          ),
        )
      }
    } catch (error) {
      console.error('Failed to resolve anomaly:', error)
    }
  }

  const handleDismiss = (id: string) => {
    setAnomalies((prev) =>
      prev.map((anomaly) => (anomaly.id === id ? { ...anomaly, status: "dismissed" as const } : anomaly)),
    )
  }

  const handleViewDetails = (anomaly: Anomaly) => {
    setSelectedAnomaly(anomaly)
    setIsModalOpen(true)
  }

  const severityCounts = anomalies.reduce(
    (acc, anomaly) => {
      acc[anomaly.severity] = (acc[anomaly.severity] || 0) + 1
      return acc
    },
    {} as Record<string, number>,
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Anomaly Management</h1>
        <p className="text-muted-foreground">Monitor, analyze, and resolve system anomalies with AI-powered insights</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-red-500/20 bg-red-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-red-400 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Critical
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-400">{severityCounts.critical || 0}</div>
          </CardContent>
        </Card>

        <Card className="border-orange-500/20 bg-orange-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-orange-400 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Major
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-400">{severityCounts.major || 0}</div>
          </CardContent>
        </Card>

        <Card className="border-yellow-500/20 bg-yellow-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-yellow-400 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Minor
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{severityCounts.minor || 0}</div>
          </CardContent>
        </Card>

        <Card className="border-blue-500/20 bg-blue-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-blue-400 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Info
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">{severityCounts.info || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search anomalies by ID, type, or service..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-full md:w-40">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="major">Major</SelectItem>
                <SelectItem value="minor">Minor</SelectItem>
                <SelectItem value="info">Info</SelectItem>
              </SelectContent>
            </Select>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="acknowledged">Acknowledged</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="dismissed">Dismissed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Anomalies Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {isLoading ? (
          <div className="col-span-full text-center py-12">
            <Loader2 className="h-12 w-12 text-primary animate-spin" />
            <p className="text-muted-foreground mt-4">Loading anomalies...</p>
          </div>
        ) : error ? (
          <div className="col-span-full text-center py-12 text-red-500">
            <AlertTriangle className="h-12 w-12 mb-4" />
            <p>{error}</p>
          </div>
        ) : filteredAnomalies.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <CheckCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No anomalies found</h3>
              <p className="text-muted-foreground">
                {searchTerm || severityFilter !== "all" || statusFilter !== "all"
                  ? "Try adjusting your filters or search terms"
                  : "All systems are running smoothly"}
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredAnomalies.map((anomaly) => (
            <AnomalyCard
              key={anomaly.id}
              anomaly={anomaly}
              onAcknowledge={handleAcknowledge}
              onResolve={handleResolve}
              onDismiss={handleDismiss}
              onViewDetails={handleViewDetails}
            />
          ))
        )}
      </div>

      {/* Details Modal */}
      <AnomalyDetailsModal
        anomaly={selectedAnomaly}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAcknowledge={handleAcknowledge}
        onResolve={handleResolve}
        onDismiss={handleDismiss}
      />
    </div>
  )
}
