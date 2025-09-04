"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { AnomalyCard, Anomaly as AnomalyCardAnomaly } from "@/components/anomaly-card"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { apiClient, Anomaly as ApiAnomaly } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { RefreshCw, AlertTriangle, CheckCircle } from "lucide-react"

// Mapping function to convert API anomaly to component anomaly
const mapApiAnomalyToCardAnomaly = (apiAnomaly: ApiAnomaly): AnomalyCardAnomaly => {
  return {
    id: apiAnomaly.id,
    type: apiAnomaly.title,
    severity: apiAnomaly.severity === 'critical' ? 'critical' : 
              apiAnomaly.severity === 'high' ? 'major' : 
              apiAnomaly.severity === 'medium' ? 'minor' : 'info',
    timestamp: apiAnomaly.detected_at,
    service: apiAnomaly.source,
    description: apiAnomaly.description,
    status: apiAnomaly.status,
    aiConfidence: apiAnomaly.metrics?.confidence || undefined,
    rootCause: apiAnomaly.metrics?.root_cause || undefined,
    acknowledgedBy: apiAnomaly.metrics?.acknowledged_by || undefined,
    resolvedAt: apiAnomaly.status === 'resolved' ? apiAnomaly.updated_at : undefined,
  }
}

export default function HomePage() {
  const router = useRouter()
  const [anomalies, setAnomalies] = useState<ApiAnomaly[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchAnomalies = async () => {
    try {
      setError(null)
      const data = await apiClient.getAnomalies()
      setAnomalies(data)
    } catch (err) {
      console.error('Failed to fetch anomalies:', err)
      setError('Failed to load anomalies. Please try again.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchAnomalies()
  }, [])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchAnomalies()
  }

  const handleAcknowledge = async (id: string) => {
    try {
      await apiClient.acknowledgeAnomaly(id)
      // Refresh the anomalies list to get updated status
      fetchAnomalies()
    } catch (err) {
      console.error('Failed to acknowledge anomaly:', err)
    }
  }

  const handleResolve = async (id: string) => {
    try {
      await apiClient.resolveAnomaly(id)
      // Refresh the anomalies list to get updated status
      fetchAnomalies()
    } catch (err) {
      console.error('Failed to resolve anomaly:', err)
    }
  }

  const handleDismiss = async (id: string) => {
    try {
      await apiClient.dismissAnomaly(id)
      // Refresh the anomalies list to get updated status
      fetchAnomalies()
    } catch (err) {
      console.error('Failed to dismiss anomaly:', err)
    }
  }

  const handleViewDetails = (anomaly: AnomalyCardAnomaly) => {
    router.push(`/anomalies/${anomaly.id}`)
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground">
                Monitor and manage system anomalies in real-time
              </p>
            </div>
            <Button 
              onClick={handleRefresh} 
              disabled={refreshing}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-4">
                <RefreshCw className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
                <p className="text-muted-foreground">Loading anomalies...</p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-4">
                <AlertTriangle className="h-8 w-8 mx-auto text-destructive" />
                <p className="text-destructive">{error}</p>
                <Button onClick={handleRefresh} variant="outline">
                  Try Again
                </Button>
              </div>
            </div>
          )}

          {/* Anomalies List */}
          {!loading && !error && (
            <div className="space-y-4">
              {anomalies.length === 0 ? (
                <div className="text-center py-12">
                  <div className="space-y-4">
                    <div className="p-4 rounded-full bg-green-100 dark:bg-green-900/20 w-fit mx-auto">
                      <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold">All Clear!</h3>
                      <p className="text-muted-foreground">
                        No active anomalies detected. Your system is running smoothly.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {anomalies.map((anomaly) => (
                    <AnomalyCard
                      key={anomaly.id}
                      anomaly={mapApiAnomalyToCardAnomaly(anomaly)}
                      onAcknowledge={handleAcknowledge}
                      onResolve={handleResolve}
                      onDismiss={handleDismiss}
                      onViewDetails={handleViewDetails}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
