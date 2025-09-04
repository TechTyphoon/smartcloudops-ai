"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Activity, 
  Brain, 
  Database, 
  GitBranch, 
  Layers, 
  TrendingUp,
  Users,
  Zap
} from "lucide-react"
import { ErrorBoundary } from "@/components/ui/error-boundary"
import { ExperimentsPanel } from "@/components/mlops/experiments-panel"
import { ModelsPanel } from "@/components/mlops/models-panel"
import { DataPipelinePanel } from "@/components/mlops/data-pipeline-panel"
import { MLOpsOverview } from "@/components/mlops/mlops-overview"
import { MLOpsStatusBar } from "@/components/mlops/mlops-status-bar"

export default function MLOpsPage() {
  const [activeTab, setActiveTab] = useState("overview")

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
          <div className="flex items-center justify-between space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">MLOps Platform</h2>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">
                <Activity className="w-3 h-3 mr-1" />
                Live
              </Badge>
            </div>
          </div>
          
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="experiments" className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Experiments
              </TabsTrigger>
              <TabsTrigger value="models" className="flex items-center gap-2">
                <Layers className="w-4 h-4" />
                Models
              </TabsTrigger>
              <TabsTrigger value="data" className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                Data Pipeline
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4">
              <ErrorBoundary>
                <MLOpsOverview />
              </ErrorBoundary>
            </TabsContent>
            
            <TabsContent value="experiments" className="space-y-4">
              <ErrorBoundary>
                <ExperimentsPanel />
              </ErrorBoundary>
            </TabsContent>
            
            <TabsContent value="models" className="space-y-4">
              <ErrorBoundary>
                <ModelsPanel />
              </ErrorBoundary>
            </TabsContent>
            
            <TabsContent value="data" className="space-y-4">
              <ErrorBoundary>
                <DataPipelinePanel />
              </ErrorBoundary>
            </TabsContent>
          </Tabs>
          
          {/* Status Bar */}
          <MLOpsStatusBar className="mt-4" />
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
