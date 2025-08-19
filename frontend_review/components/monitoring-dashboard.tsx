"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Activity, Cpu, HardDrive, MemoryStick, Network, Server, AlertTriangle, CheckCircle, Clock, Loader2 } from "lucide-react"
import { apiClient } from "@/lib/api"

interface SystemMetric {
  name: string
  value: number
  status: "healthy" | "warning" | "critical"
  unit: string
  icon: React.ReactNode
}

interface ServiceStatus {
  name: string
  status: "running" | "stopped" | "error"
  uptime: string
  responseTime: number
}

export function MonitoringDashboard() {
  const [metrics, setMetrics] = useState<SystemMetric[]>([])
  const [services, setServices] = useState<ServiceStatus[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch real data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Fetch system status and metrics
        const [statusResponse, metricsResponse] = await Promise.all([
          apiClient.getSystemStatus(),
          apiClient.getMetrics()
        ])

        if (statusResponse.status === 'success' && metricsResponse.status === 'success') {
          // Process real metrics data
          const realMetrics: SystemMetric[] = [
            { 
              name: "CPU Usage", 
              value: Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? metricsResponse.data[0].cpu_usage : 0, 
              status: getStatusFromValue(Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? metricsResponse.data[0].cpu_usage : 0), 
              unit: "%", 
              icon: <Cpu className="w-4 h-4" /> 
            },
            { 
              name: "Memory", 
              value: Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? metricsResponse.data[0].memory_usage : 0, 
              status: getStatusFromValue(Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? metricsResponse.data[0].memory_usage : 0), 
              unit: "%", 
              icon: <MemoryStick className="w-4 h-4" /> 
            },
            { 
              name: "Disk Usage", 
              value: Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? metricsResponse.data[0].disk_usage : 0, 
              status: getStatusFromValue(Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? metricsResponse.data[0].disk_usage : 0), 
              unit: "%", 
              icon: <HardDrive className="w-4 h-4" /> 
            },
            { 
              name: "Network I/O", 
              value: Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? (metricsResponse.data[0].network_in + metricsResponse.data[0].network_out) / 1000000 : 0, 
              status: getStatusFromValue(Array.isArray(metricsResponse.data) && metricsResponse.data.length > 0 ? (metricsResponse.data[0].network_in + metricsResponse.data[0].network_out) / 1000000 : 0), 
              unit: "Mbps", 
              icon: <Network className="w-4 h-4" /> 
            },
          ]

          setMetrics(realMetrics)

          // Process service status from system status
          if (statusResponse.data?.services) {
            const realServices: ServiceStatus[] = Object.entries(statusResponse.data.services).map(([name, service]: [string, any]) => ({
              name,
              status: service.status || 'unknown',
              uptime: service.uptime || '0%',
              responseTime: service.response_time || 0
            }))
            setServices(realServices)
          }
        } else {
          setError('Failed to fetch system data')
        }
      } catch (err) {
        setError('Error connecting to backend')
        console.error('Failed to fetch monitoring data:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()

    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 30000) // Poll every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const getStatusFromValue = (value: number): "healthy" | "warning" | "critical" => {
    if (value > 80) return "critical"
    if (value > 60) return "warning"
    return "healthy"
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
      case "running":
        return "status-healthy"
      case "warning":
        return "status-warning"
      case "critical":
      case "error":
        return "status-critical"
      default:
        return "status-info"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
      case "running":
        return <CheckCircle className="w-4 h-4" />
      case "warning":
        return <AlertTriangle className="w-4 h-4" />
      case "critical":
      case "error":
        return <AlertTriangle className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                <div className="h-4 w-4 bg-muted animate-pulse rounded" />
              </CardHeader>
              <CardContent>
                <div className="h-8 w-16 bg-muted animate-pulse rounded mb-2" />
                <div className="h-2 w-full bg-muted animate-pulse rounded mb-2" />
                <div className="h-6 w-20 bg-muted animate-pulse rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Card className="glass-card">
          <CardContent className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <p className="text-red-400 font-medium">Connection Error</p>
            <p className="text-sm text-muted-foreground mt-2">{error}</p>
            <p className="text-xs text-muted-foreground mt-1">Check if backend is running on port 5000</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => (
          <Card key={metric.name} className="glass-card enterprise-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.name}</CardTitle>
              {metric.icon}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metric.value > 0 ? `${metric.value.toFixed(1)}${metric.unit}` : `--${metric.unit}`}
              </div>
              <Progress value={metric.value} className="mt-2" />
              <Badge className={`mt-2 ${getStatusColor(metric.status)}`}>
                {getStatusIcon(metric.status)}
                <span className="ml-1 capitalize">{metric.status}</span>
              </Badge>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Service Status */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="w-5 h-5" />
            Service Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          {services.length > 0 ? (
            <div className="space-y-4">
              {services.map((service) => (
                <div key={service.name} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(service.status)}`} />
                    <div>
                      <p className="font-medium">{service.name}</p>
                      <p className="text-sm text-muted-foreground">Uptime: {service.uptime}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{service.responseTime}ms</p>
                    <Badge className={getStatusColor(service.status)}>
                      {getStatusIcon(service.status)}
                      <span className="ml-1 capitalize">{service.status}</span>
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Server className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No services configured</p>
              <p className="text-sm text-muted-foreground">Connect your backend to see service status</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
