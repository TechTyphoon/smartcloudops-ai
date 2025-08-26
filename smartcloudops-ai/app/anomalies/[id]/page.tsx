"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { apiClient, Anomaly } from "@/lib/api-client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Separator } from "@/components/ui/separator"
import { 
  ArrowLeft, 
  AlertTriangle, 
  Clock, 
  CheckCircle, 
  X, 
  RefreshCw,
  Calendar,
  Activity,
  Tag,
  Info
} from "lucide-react"
import { cn } from "@/lib/utils"

const severityConfig = {
  critical: {
    color: "bg-red-500/10 border-red-500/20 text-red-400",
    badge: "bg-red-500/20 text-red-300 border-red-500/30",
    icon: AlertTriangle,
  },
  high: {
    color: "bg-orange-500/10 border-orange-500/20 text-orange-400",
    badge: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    icon: AlertTriangle,
  },
  medium: {
    color: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400",
    badge: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    icon: Clock,
  },
  low: {
    color: "bg-blue-500/10 border-blue-500/20 text-blue-400",
    badge: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    icon: Info,
  },
}

const statusConfig = {
  open: {
    color: "bg-red-500/20 text-red-300 border-red-500/30",
    icon: AlertTriangle,
  },
  acknowledged: {
    color: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    icon: Clock,
  },
  resolved: {
    color: "bg-green-500/20 text-green-300 border-green-500/30",
    icon: CheckCircle,
  },
  dismissed: {
    color: "bg-gray-500/20 text-gray-300 border-gray-500/30",
    icon: X,
  },
}

export default function AnomalyDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  const [anomaly, setAnomaly] = useState<Anomaly | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)

  const fetchAnomaly = async () => {
    if (!id) return
    
    try {
      setError(null)
      setLoading(true)
      const data = await apiClient.getAnomaly(id)
      setAnomaly(data)
    } catch (err) {
      console.error('Failed to fetch anomaly:', err)
      setError('Failed to load anomaly details. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnomaly()
  }, [id])

  const handleAction = async (action: () => Promise<void>) => {
    if (!anomaly) return
    
    try {
      setProcessing(true)
      await action()
      // Refresh the anomaly data after action
      await fetchAnomaly()
    } catch (err) {
      console.error('Action failed:', err)
    } finally {
      setProcessing(false)
    }
  }

  const handleAcknowledge = () => handleAction(() => apiClient.acknowledgeAnomaly(anomaly!.id))
  const handleResolve = () => handleAction(() => apiClient.resolveAnomaly(anomaly!.id))
  const handleDismiss = () => handleAction(() => apiClient.dismissAnomaly(anomaly!.id))

  const handleBack = () => {
    router.push('/')
  }

  if (loading) {
    return (
      <ProtectedRoute>
        <DashboardLayout>
          <div className="flex items-center justify-center py-12">
            <div className="text-center space-y-4">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
              <p className="text-muted-foreground">Loading anomaly details...</p>
            </div>
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    )
  }

  if (error || !anomaly) {
    return (
      <ProtectedRoute>
        <DashboardLayout>
          <div className="flex items-center justify-center py-12">
            <div className="text-center space-y-4">
              <AlertTriangle className="h-8 w-8 mx-auto text-destructive" />
              <p className="text-destructive">{error || 'Anomaly not found'}</p>
              <Button onClick={handleBack} variant="outline">
                Back to Dashboard
              </Button>
            </div>
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    )
  }

  const severity = severityConfig[anomaly.severity]
  const status = statusConfig[anomaly.status]
  const SeverityIcon = severity.icon
  const StatusIcon = status.icon

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button onClick={handleBack} variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-3xl font-bold">Anomaly Details</h1>
                <p className="text-muted-foreground">ID: {anomaly.id}</p>
              </div>
            </div>
            
            {/* Action Buttons */}
            {anomaly.status === 'open' && (
              <div className="flex gap-2">
                <Button
                  onClick={handleAcknowledge}
                  disabled={processing}
                  variant="outline"
                  size="sm"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Acknowledge
                </Button>
                <Button
                  onClick={handleResolve}
                  disabled={processing}
                  variant="outline"
                  size="sm"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Resolve
                </Button>
                <Button
                  onClick={handleDismiss}
                  disabled={processing}
                  variant="outline"
                  size="sm"
                >
                  <X className="h-4 w-4 mr-2" />
                  Dismiss
                </Button>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Primary Information */}
            <div className="lg:col-span-2 space-y-6">
              {/* Anomaly Card */}
              <Card className={cn("border", severity.color)}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <SeverityIcon className="h-6 w-6" />
                        <CardTitle className="text-xl">{anomaly.title}</CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className={cn("text-sm", severity.badge)}>
                          {anomaly.severity.toUpperCase()}
                        </Badge>
                        <Badge variant="outline" className={cn("text-sm", status.color)}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {anomaly.status.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">{anomaly.description}</p>
                  
                  {/* Tags */}
                  {anomaly.tags && anomaly.tags.length > 0 && (
                    <div className="flex items-center gap-2 mb-4">
                      <Tag className="h-4 w-4 text-muted-foreground" />
                      <div className="flex gap-1">
                        {anomaly.tags.map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Metrics Table */}
              {anomaly.metrics && Object.keys(anomaly.metrics).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      Metrics & Data
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Metric</TableHead>
                          <TableHead>Value</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {Object.entries(anomaly.metrics).map(([key, value]) => (
                          <TableRow key={key}>
                            <TableCell className="font-medium">{key}</TableCell>
                            <TableCell>
                              {typeof value === 'number' 
                                ? value.toLocaleString() 
                                : String(value)
                              }
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Timestamps */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Timeline
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm font-medium">Detected</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(anomaly.detected_at).toLocaleString()}
                    </p>
                  </div>
                  <Separator />
                  <div>
                    <p className="text-sm font-medium">Last Updated</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(anomaly.updated_at).toLocaleString()}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Source Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Info className="h-5 w-5" />
                    Source
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm font-medium">Service</p>
                  <p className="text-sm text-muted-foreground mb-4">{anomaly.source}</p>
                  
                  <p className="text-sm font-medium">Anomaly ID</p>
                  <p className="text-sm text-muted-foreground font-mono">{anomaly.id}</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
