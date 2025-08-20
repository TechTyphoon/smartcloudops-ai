import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Brain, 
  Zap, 
  Shield, 
  TrendingUp, 
  ArrowRight, 
  Play,
  BarChart3
} from 'lucide-react';

const WelcomeHero: React.FC = () => {
  return (
    <div className="space-y-12 lg:space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-8">
        {/* Logo and Title */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <div className="p-3 rounded-xl bg-primary/10 border border-primary/20">
            <Brain className="h-12 w-12 text-primary" />
          </div>
          <div className="text-left">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              SmartCloudOps AI
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground mt-2">
              AI-Powered CloudOps Intelligence Platform
            </p>
          </div>
        </div>

        {/* Description */}
        <div className="max-w-4xl mx-auto space-y-6">
          <p className="text-xl sm:text-2xl lg:text-3xl text-muted-foreground leading-relaxed font-medium">
            Transform your cloud operations with intelligent automation, real-time monitoring, and predictive analytics
          </p>
          <p className="text-base sm:text-lg lg:text-xl text-muted-foreground/80 leading-relaxed max-w-3xl mx-auto">
            Streamline your infrastructure management with AI-driven insights and automated remediation
          </p>
        </div>

        {/* Status Badge */}
        <div className="flex justify-center">
          <Badge variant="secondary" className="font-medium">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            All Systems Operational
          </Badge>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
        <Card className="group hover:shadow-lg transition-all duration-300 border-border/50 hover:border-primary/30 bg-card/50 hover:bg-card">
          <CardContent className="p-6 text-center space-y-4">
            <div className="w-12 h-12 mx-auto rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-2">AI Automation</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Intelligent workflows that adapt to your infrastructure patterns
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="group hover:shadow-lg transition-all duration-300 border-border/50 hover:border-primary/30 bg-card/50 hover:bg-card">
          <CardContent className="p-6 text-center space-y-4">
            <div className="w-12 h-12 mx-auto rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <BarChart3 className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-2">Real-time Monitoring</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Comprehensive visibility across all your cloud resources
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="group hover:shadow-lg transition-all duration-300 border-border/50 hover:border-primary/30 bg-card/50 hover:bg-card">
          <CardContent className="p-6 text-center space-y-4">
            <div className="w-12 h-12 mx-auto rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <Shield className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-2">Security First</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Proactive threat detection and automated security responses
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="group hover:shadow-lg transition-all duration-300 border-border/50 hover:border-primary/30 bg-card/50 hover:bg-card">
          <CardContent className="p-6 text-center space-y-4">
            <div className="w-12 h-12 mx-auto rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-2">Predictive Analytics</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Forecast issues before they impact your operations
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Call to Action */}
      <div className="text-center space-y-8">
        <div className="max-w-2xl mx-auto space-y-4">
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground">
            Ready to Transform Your Cloud Operations?
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed">
            Get started with intelligent automation and real-time monitoring today.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button size="lg" className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-white px-8 py-3">
            Get Started
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button variant="outline" size="lg" className="px-8 py-3">
            <Play className="mr-2 h-5 w-5" />
            Learn More
          </Button>
        </div>
      </div>
    </div>
  );
};

export default WelcomeHero;
