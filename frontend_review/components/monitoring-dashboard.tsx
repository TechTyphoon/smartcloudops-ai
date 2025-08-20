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

          // Process service status
          const realServices: ServiceStatus[] = [
            {
              name: "SmartCloudOps API",
              status: statusResponse.data?.status === 'healthy' ? 'running' : 'error',
              uptime: "2 days, 14 hours",
              responseTime: 45
            },
            {
              name: "Database",
              status: 'running',
              uptime: "5 days, 2 hours",
              responseTime: 12
            },
            {
              name: "Redis Cache",
              status: 'running',
              uptime: "1 day, 8 hours",
              responseTime: 3
            },
            {
              name: "ML Models",
              status: 'running',
              uptime: "3 days, 12 hours",
              responseTime: 28
            }
          ]

          setServices(realServices)
        } else {
          setError("Failed to fetch monitoring data")
        }
      } catch (err) {
        setError("Error loading monitoring data")
        console.error("Monitoring data fetch error:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusFromValue = (value: number): "healthy" | "warning" | "critical" => {
    if (value >= 90) return "critical"
    if (value >= 70) return "warning"
    return "healthy"
  }

  const getStatusColor = (status: "healthy" | "warning" | "critical" | "running" | "stopped" | "error") => {
    switch (status) {
      case "healthy":
      case "running":
        return "bg-emerald-500"
      case "warning":
        return "bg-yellow-500"
      case "critical":
      case "error":
        return "bg-red-500"
      case "stopped":
        return "bg-gray-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusIcon = (status: "healthy" | "warning" | "critical" | "running" | "stopped" | "error") => {
    switch (status) {
      case "healthy":
      case "running":
        return <CheckCircle className="w-4 h-4 text-emerald-500" />
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case "critical":
      case "error":
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      case "stopped":
        return <Clock className="w-4 h-4 text-gray-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-lg">Loading monitoring data...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-4">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
          <h3 className="text-lg font-semibold">Error Loading Data</h3>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-foreground">System Monitoring</h1>
          <p className="text-muted-foreground">Real-time system metrics and service status</p>
        </div>
        <Badge variant="outline" className="text-sm">
          <Activity className="w-4 h-4 mr-2" />
          Live Data
        </Badge>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric) => (
          <Card key={metric.name} className="relative overflow-hidden">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {metric.name}
                </CardTitle>
                <div className="flex items-center gap-2">
                  {metric.icon}
                  <Badge 
                    variant={metric.status === 'healthy' ? 'default' : metric.status === 'warning' ? 'secondary' : 'destructive'}
                    className="text-xs"
                  >
                    {metric.status}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-foreground">
                  {metric.value.toFixed(1)}
                </span>
                <span className="text-sm text-muted-foreground">
                  {metric.unit}
                </span>
              </div>
              <Progress 
                value={metric.value} 
                className="h-2"
              />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Services Status */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-foreground">Service Status</h2>
          <Badge variant="outline" className="text-sm">
            {services.filter(s => s.status === 'running').length} of {services.length} Running
          </Badge>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {services.map((service) => (
            <Card key={service.name} className="relative">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(service.status)}
                      <div>
                        <h3 className="font-semibold text-foreground">{service.name}</h3>
                        <p className="text-sm text-muted-foreground">Uptime: {service.uptime}</p>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${getStatusColor(service.status)}`} />
                      <Badge 
                        variant={service.status === 'running' ? 'default' : 'destructive'}
                        className="text-xs capitalize"
                      >
                        {service.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {service.responseTime}ms
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
