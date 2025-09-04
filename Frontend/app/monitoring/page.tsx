"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { MonitoringDashboard } from "@/components/monitoring-dashboard"
import { apiClient, SystemHealth, SystemMetrics } from "@/lib/api-client"
import { RefreshCw, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function MonitoringPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchMonitoringData = async () => {
    try {
      setError(null)
      setLoading(true)
      
      // Fetch both health and metrics data in parallel
      const [healthData, metricsData] = await Promise.all([
        apiClient.getHealth(),
        apiClient.getMetrics()
      ])
      
      setHealth(healthData)
      setMetrics(metricsData)
    } catch (err) {
      console.error('Failed to fetch monitoring data:', err)
      setError('Failed to load monitoring data. Please try again.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchMonitoringData()
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchMonitoringData, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchMonitoringData()
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">System Monitoring</h1>
              <p className="text-muted-foreground">Real-time infrastructure health and performance metrics</p>
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
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="py-6">
                    <div className="h-4 bg-muted rounded w-24 mb-2"></div>
                    <div className="h-8 bg-muted rounded w-16 mb-2"></div>
                    <div className="h-2 bg-muted rounded w-full"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <Card className="animate-pulse">
              <CardContent className="py-6">
                <div className="h-6 bg-muted rounded w-32 mb-4"></div>
                <div className="space-y-3">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-12 bg-muted rounded"></div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">System Monitoring</h1>
              <p className="text-muted-foreground">Real-time infrastructure health and performance metrics</p>
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
          
          {/* Error State */}
          <Card className="border-red-500/20">
            <CardContent className="py-8 text-center">
              <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Failed to Load Monitoring Data</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={handleRefresh} variant="outline">
                Try Again
              </Button>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">System Monitoring</h1>
            <p className="text-muted-foreground">Real-time infrastructure health and performance metrics</p>
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
        
        {/* Live Monitoring Dashboard */}
        <MonitoringDashboard 
          health={health}
          metrics={metrics}
        />
      </div>
    </DashboardLayout>
  )
}
