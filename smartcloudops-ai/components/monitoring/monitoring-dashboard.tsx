"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { RealTimeStatus } from "@/components/real-time-status"
import { useRealTimeMetrics } from "@/hooks/use-real-time-metrics"
import {
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  Network,
  Server,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw,
} from "lucide-react"

interface ServiceStatus {
  name: string
  status: "running" | "stopped" | "error"
  uptime: string
  responseTime: number
}

export function MonitoringDashboard() {
  const { metrics, connectionStatus, refreshMetrics, isRealTime, error } = useRealTimeMetrics({
    enableWebSocket: true,
    fallbackInterval: 5000,
  })

  const [services] = useState<ServiceStatus[]>([
    { name: "Web Server", status: "running", uptime: "99.9%", responseTime: 120 },
    { name: "Database", status: "running", uptime: "99.8%", responseTime: 45 },
    { name: "Cache Layer", status: "running", uptime: "99.9%", responseTime: 12 },
    { name: "Message Queue", status: "error", uptime: "95.2%", responseTime: 0 },
  ])

  const systemMetrics = [
    {
      name: "CPU Usage",
      value: metrics.cpu.value,
      status: metrics.cpu.status,
      unit: "%",
      icon: <Cpu className="w-4 h-4" />,
    },
    {
      name: "Memory",
      value: metrics.memory.value,
      status: metrics.memory.status,
      unit: "%",
      icon: <MemoryStick className="w-4 h-4" />,
    },
    {
      name: "Disk Usage",
      value: metrics.disk.value,
      status: metrics.disk.status,
      unit: "%",
      icon: <HardDrive className="w-4 h-4" />,
    },
    {
      name: "Network I/O",
      value: metrics.network.value,
      status: metrics.network.status,
      unit: "Mbps",
      icon: <Network className="w-4 h-4" />,
    },
  ]

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

  return (
    <div className="space-y-6">
      {/* Header with Real-time Status */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">System Monitoring</h1>
          <p className="text-muted-foreground">Real-time infrastructure health and performance metrics</p>
        </div>
        <div className="flex items-center gap-3">
          <RealTimeStatus status={connectionStatus} error={error} />
          <Button variant="outline" size="sm" onClick={refreshMetrics}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {systemMetrics.map((metric) => (
          <Card key={metric.name} className="glass-card enterprise-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.name}</CardTitle>
              {metric.icon}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metric.value.toFixed(1)}
                {metric.unit}
              </div>
              <Progress value={metric.value} className="mt-2" />
              <Badge className={`mt-2 ${getStatusColor(metric.status)}`}>
                {getStatusIcon(metric.status)}
                <span className="ml-1 capitalize">{metric.status}</span>
              </Badge>
              {isRealTime && (
                <div className="text-xs text-muted-foreground mt-1">
                  Last updated: {new Date(metrics.cpu.timestamp).toLocaleTimeString()}
                </div>
              )}
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
          <div className="space-y-4">
            {services.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-3">
                  <Badge className={getStatusColor(service.status)}>
                    {getStatusIcon(service.status)}
                    <span className="ml-1 capitalize">{service.status}</span>
                  </Badge>
                  <span className="font-medium">{service.name}</span>
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {service.uptime}
                  </div>
                  <div className="flex items-center gap-1">
                    <Activity className="w-3 h-3" />
                    {service.responseTime}ms
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Recent Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 rounded-lg border border-red-500/30 bg-red-500/10">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <div className="flex-1">
                <p className="font-medium text-red-400">High Network Traffic</p>
                <p className="text-sm text-muted-foreground">Network I/O exceeding 85% threshold</p>
              </div>
              <span className="text-xs text-muted-foreground">2 min ago</span>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg border border-amber-500/30 bg-amber-500/10">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <div className="flex-1">
                <p className="font-medium text-amber-400">Memory Usage Warning</p>
                <p className="text-sm text-muted-foreground">Memory usage above 70%</p>
              </div>
              <span className="text-xs text-muted-foreground">5 min ago</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
