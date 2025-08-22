import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Brain, Cloud, Zap, Shield } from "lucide-react"

export function WelcomeHero() {
  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3 mb-6">
          <div className="p-3 rounded-xl bg-primary/10 border border-primary/20">
            <Brain className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
            SmartCloudOps AI
          </h1>
        </div>

        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">AI-Powered CloudOps Intelligence</p>

        <Badge variant="secondary" className="text-sm px-4 py-2">
          Enterprise Cloud Operations Platform
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass-card p-6 transition-all duration-200 ease-in-out hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-chart-1/20 border border-chart-1/30">
              <Brain className="h-5 w-5 text-chart-1" />
            </div>
            <h3 className="font-semibold">AI Intelligence</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Advanced AI-driven insights and automated decision making for your cloud infrastructure.
          </p>
        </Card>

        <Card className="glass-card p-6 transition-all duration-200 ease-in-out hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-chart-2/20 border border-chart-2/30">
              <Cloud className="h-5 w-5 text-chart-2" />
            </div>
            <h3 className="font-semibold">Cloud Operations</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Comprehensive monitoring and management of multi-cloud environments at enterprise scale.
          </p>
        </Card>

        <Card className="glass-card p-6 transition-all duration-200 ease-in-out hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-chart-5/20 border border-chart-5/30">
              <Zap className="h-5 w-5 text-chart-5" />
            </div>
            <h3 className="font-semibold">Real-time Analytics</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Live performance metrics and instant alerting for proactive infrastructure management.
          </p>
        </Card>

        <Card className="glass-card p-6 transition-all duration-200 ease-in-out hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-primary/20 border border-primary/30">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <h3 className="font-semibold">Enterprise Security</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Fortune 500-grade security controls with compliance monitoring and threat detection.
          </p>
        </Card>
      </div>
    </div>
  )
}
