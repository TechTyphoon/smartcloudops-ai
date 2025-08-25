import { DashboardLayout } from "@/components/dashboard-layout"
import { MonitoringDashboard } from "@/components/monitoring-dashboard"

export default function MonitoringPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Monitoring</h1>
          <p className="text-muted-foreground">Real-time infrastructure health and performance metrics</p>
        </div>
        <MonitoringDashboard />
      </div>
    </DashboardLayout>
  )
}
