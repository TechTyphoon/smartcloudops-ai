import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Brain, Cloud, Zap, Shield, ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"

export function WelcomeHero() {
  const features = [
    {
      icon: Brain,
      title: "AI Intelligence",
      description: "Advanced AI-driven insights and automated decision making for your cloud infrastructure.",
      color: "chart-1",
      gradient: "from-chart-1/20 to-chart-1/10"
    },
    {
      icon: Cloud,
      title: "Cloud Operations",
      description: "Comprehensive monitoring and management of multi-cloud environments at enterprise scale.",
      color: "chart-2",
      gradient: "from-chart-2/20 to-chart-2/10"
    },
    {
      icon: Zap,
      title: "Real-time Analytics",
      description: "Live performance metrics and instant alerting for proactive infrastructure management.",
      color: "chart-5",
      gradient: "from-chart-5/20 to-chart-5/10"
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "Fortune 500-grade security controls with compliance monitoring and threat detection.",
      color: "primary",
      gradient: "from-primary/20 to-primary/10"
    }
  ]

  return (
    <div className="space-y-8 lg:space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="p-4 rounded-2xl bg-primary/10 border border-primary/20 shadow-lg">
            <Brain className="h-10 w-10 text-primary" aria-hidden="true" />
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent leading-tight">
            SmartCloudOps AI
          </h1>
        </div>

        <div className="max-w-3xl mx-auto space-y-4">
          <p className="text-xl sm:text-2xl text-muted-foreground leading-relaxed">
            AI-Powered CloudOps Intelligence Platform
          </p>
          <p className="text-base sm:text-lg text-muted-foreground/80 leading-relaxed">
            Transform your cloud operations with intelligent automation, real-time monitoring, and predictive analytics
          </p>
        </div>

        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Badge variant="secondary" className="text-sm px-6 py-3 text-base">
            Enterprise Cloud Operations Platform
          </Badge>
          <Badge variant="outline" className="text-sm px-6 py-3 text-base">
            AI-Powered Intelligence
          </Badge>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon
          return (
            <Card 
              key={feature.title}
              className={cn(
                "glass-card p-6 transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-xl group",
                "focus-within:scale-105 focus-within:shadow-xl focus-within:ring-2 focus-within:ring-ring"
              )}
              tabIndex={0}
              role="article"
              aria-labelledby={`feature-${index}-title`}
              aria-describedby={`feature-${index}-description`}
            >
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "p-3 rounded-xl border shadow-sm transition-all duration-300 group-hover:scale-110",
                    `bg-gradient-to-br ${feature.gradient}`,
                    `border-${feature.color}/30`
                  )}>
                    <Icon className={cn("h-6 w-6", `text-${feature.color}`)} aria-hidden="true" />
                  </div>
                  <h3 
                    id={`feature-${index}-title`}
                    className="font-semibold text-lg leading-tight"
                  >
                    {feature.title}
                  </h3>
                </div>
                
                <p 
                  id={`feature-${index}-description`}
                  className="text-sm text-muted-foreground leading-relaxed"
                >
                  {feature.description}
                </p>

                <div className="flex items-center gap-2 text-sm text-primary font-medium group-hover:gap-3 transition-all duration-300">
                  <span>Learn more</span>
                  <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Call to Action */}
      <div className="text-center space-y-6 pt-8">
        <div className="max-w-2xl mx-auto space-y-4">
          <h2 className="text-2xl sm:text-3xl font-bold">
            Ready to Transform Your Cloud Operations?
          </h2>
          <p className="text-muted-foreground leading-relaxed">
            Experience the future of cloud management with AI-powered insights and automated remediation
          </p>
        </div>
        
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <button className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors duration-200 enterprise-focus">
            Get Started
            <ArrowRight className="h-4 w-4" />
          </button>
          <button className="inline-flex items-center gap-2 px-6 py-3 border border-border bg-background text-foreground rounded-lg font-medium hover:bg-muted transition-colors duration-200 enterprise-focus">
            View Demo
          </button>
        </div>
      </div>
    </div>
  )
}
