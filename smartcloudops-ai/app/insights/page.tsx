"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SLAIndicator, type SLAMetric } from "@/components/sla-indicator"
import { CostOptimizationCard, type CostOptimization } from "@/components/cost-optimization-card"
import { ServiceDependencyGraph, type ServiceNode } from "@/components/service-dependency-graph"
import { AuditLog, type AuditLogEntry } from "@/components/audit-log"
import { BarChart, TrendingUp, DollarSign, Network, FileText } from "lucide-react"

// TODO: Replace with real data from backend API
const mockSLAMetrics: SLAMetric[] = []

// TODO: Replace with real data from backend API
const mockCostOptimizations: CostOptimization[] = []

// TODO: Replace with real data from backend API
const mockServices: ServiceNode[] = [
  {
    id: "payment-service",
    name: "Payment Service",
    type: "api",
    status: "warning",
    dependencies: ["postgres-db", "stripe-api"],
  },
  {
    id: "postgres-db",
    name: "PostgreSQL",
    type: "database",
    status: "critical",
    dependencies: [],
  },
  {
    id: "redis-cache",
    name: "Redis Cache",
    type: "cache",
    status: "healthy",
    dependencies: [],
  },
  {
    id: "stripe-api",
    name: "Stripe API",
    type: "external",
    status: "healthy",
    dependencies: [],
  },
]

// TODO: Replace with real data from backend API
const mockAuditEntries: AuditLogEntry[] = []

export default function InsightsPage() {
  const handleImplementOptimization = (id: string) => {
    console.log("[v0] Implementing cost optimization:", id)
    // Implementation logic would go here
  }

  const totalPotentialSavings = mockCostOptimizations.reduce((sum, opt) => sum + opt.potentialSavings, 0)
  const healthySLAs = mockSLAMetrics.filter((m) => m.status === "healthy").length
  const criticalServices = mockServices.filter((s) => s.status === "critical").length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <BarChart className="h-8 w-8 text-teal-400" />
          Advanced Insights
        </h1>
        <p className="text-muted-foreground">Enterprise analytics, SLA monitoring, and cost optimization insights</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-teal-500/20 bg-teal-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-teal-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Healthy SLAs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-teal-400">
              {healthySLAs}/{mockSLAMetrics.length}
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-500/20 bg-green-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-green-400 flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Potential Savings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">${totalPotentialSavings.toLocaleString()}</div>
          </CardContent>
        </Card>

        <Card className="border-red-500/20 bg-red-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-red-400 flex items-center gap-2">
              <Network className="h-4 w-4" />
              Critical Services
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-400">{criticalServices}</div>
          </CardContent>
        </Card>

        <Card className="border-blue-500/20 bg-blue-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-blue-400 flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Audit Events
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">{mockAuditEntries.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* SLA Indicators */}
      <div>
        <h2 className="text-xl font-semibold mb-4 text-teal-400">SLA/SLI Indicators</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {mockSLAMetrics.map((metric) => (
            <SLAIndicator key={metric.id} metric={metric} />
          ))}
        </div>
      </div>

      {/* Cost Optimizations */}
      <div>
        <h2 className="text-xl font-semibold mb-4 text-teal-400">AI-Driven Cost Optimizations</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {mockCostOptimizations.map((optimization) => (
            <CostOptimizationCard
              key={optimization.id}
              optimization={optimization}
              onImplement={handleImplementOptimization}
            />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Service Dependencies */}
        <ServiceDependencyGraph services={mockServices} />

        {/* Audit Log */}
        <AuditLog entries={mockAuditEntries} />
      </div>
    </div>
  )
}
