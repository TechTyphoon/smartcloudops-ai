"use client"

import { useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { 
  Activity, 
  Brain, 
  Database, 
  Layers, 
  TrendingUp,
  Users,
  Zap,
  AlertTriangle,
  RefreshCw,
  Play,
  Pause
} from "lucide-react"
import { useMLOpsStats, useRealTime } from "@/lib/stores/mlops-store"

interface MLOpsOverviewProps {}

export function MLOpsOverview({}: MLOpsOverviewProps) {
  const { statistics, loading, error, fetch } = useMLOpsStats()
  const { enabled: realTimeEnabled, start: startRealTime, stop: stopRealTime } = useRealTime()

  useEffect(() => {
    // Initial fetch
    fetch()
    
    // Start real-time updates automatically
    startRealTime()
    
    // Cleanup on unmount
    return () => stopRealTime()
  }, [])

  const handleRefresh = async () => {
    await fetch(true) // Force refresh
  }

  const toggleRealTime = () => {
    if (realTimeEnabled) {
      stopRealTime()
    } else {
      startRealTime()
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {/* Loading Header */}
        <div className="flex items-center justify-between">
          <div className="h-6 bg-muted rounded w-32 animate-pulse"></div>
          <div className="flex gap-2">
            <div className="h-9 bg-muted rounded w-24 animate-pulse"></div>
            <div className="h-9 bg-muted rounded w-32 animate-pulse"></div>
          </div>
        </div>
        
        {/* Loading Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="h-4 bg-muted rounded w-24"></div>
                <div className="h-4 w-4 bg-muted rounded"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted rounded w-16 mb-2"></div>
                <div className="h-3 bg-muted rounded w-32"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="col-span-full">
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">
              {error === 'MLOps service unavailable' ? 
                'MLOps service is starting up. Please wait a moment...' : 
                `Error: ${error}`
              }
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!statistics) {
    return (
      <Card className="col-span-full">
        <CardContent className="flex items-center justify-center py-8">
          <p className="text-sm text-muted-foreground">No statistics available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with Real-time Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">MLOps Overview</h3>
          {realTimeEnabled && (
            <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">
              <Activity className="w-3 h-3 mr-1 animate-pulse" />
              Live
            </Badge>
          )}
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button 
            variant={realTimeEnabled ? "default" : "outline"} 
            size="sm" 
            onClick={toggleRealTime}
          >
            {realTimeEnabled ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                Stop Live
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Live
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Experiments</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.experiments.total}</div>
            <p className="text-xs text-muted-foreground">
              {statistics.experiments.active} active, {statistics.experiments.completed} completed
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Registered Models</CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.models.total}</div>
            <p className="text-xs text-muted-foreground">
              {statistics.models.production} in production
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Versions</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.data_pipeline_stats.total_versions}</div>
            <p className="text-xs text-muted-foreground">
              Avg. quality: {(statistics.data_pipeline_stats.average_quality_score * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Datasets</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.data_pipeline_stats.total_datasets}</div>
            <p className="text-xs text-muted-foreground">
              Managed datasets
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Status Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Experiment Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Active Experiments</span>
                <Badge variant="default">{statistics.experiments.active}</Badge>
              </div>
              <Progress 
                value={(statistics.experiments.active / Math.max(statistics.experiments.total, 1)) * 100} 
                className="h-2" 
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Success Rate</span>
                <span className="text-sm font-medium">
                  {statistics.experiments.total > 0 
                    ? ((statistics.experiments.completed / statistics.experiments.total) * 100).toFixed(1)
                    : 0
                  }%
                </span>
              </div>
              <Progress 
                value={statistics.experiments.total > 0 
                  ? (statistics.experiments.completed / statistics.experiments.total) * 100
                  : 0
                } 
                className="h-2" 
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5" />
              Model Deployment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Production Models</span>
                <Badge variant="default" className="bg-green-500">{statistics.models.production}</Badge>
              </div>
              <Progress 
                value={(statistics.models.production / Math.max(statistics.models.total, 1)) * 100} 
                className="h-2" 
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Staging Models</span>
                <Badge variant="secondary">{statistics.models.staging}</Badge>
              </div>
              <Progress 
                value={(statistics.models.staging / Math.max(statistics.models.total, 1)) * 100} 
                className="h-2" 
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Quality Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Data Quality Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(statistics.data_pipeline_stats.by_quality_status || {}).map(([status, count]) => (
              <div key={status} className="text-center">
                <div className="text-2xl font-bold">{count}</div>
                <div className="text-xs text-muted-foreground capitalize">{status}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* MLflow Integration Status */}
      {statistics.mlflow_experiments && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              MLflow Integration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">MLflow Experiments</p>
                <p className="text-2xl font-bold">{statistics.mlflow_experiments.total}</p>
              </div>
              <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20">
                <Activity className="w-3 h-3 mr-1" />
                Connected
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
