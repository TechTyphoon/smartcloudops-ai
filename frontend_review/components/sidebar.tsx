"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { MessageSquare, Activity, AlertTriangle, Wrench, Settings, ChevronLeft, Cloud, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface SidebarProps {
  isCollapsed: boolean
  onToggle: () => void
  isMobileOpen?: boolean
  onMobileClose?: () => void
}

const navigation = [
  {
    name: "ChatOps",
    href: "/chatops",
    icon: MessageSquare,
    description: "AI-powered operations chat",
  },
  {
    name: "Monitoring",
    href: "/monitoring",
    icon: Activity,
    description: "System health & metrics",
  },
  {
    name: "Anomalies",
    href: "/anomalies",
    icon: AlertTriangle,
    description: "Detect & analyze issues",
  },
  {
    name: "Remediation",
    href: "/remediation",
    icon: Wrench,
    description: "Automated fixes & actions",
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
    description: "Platform configuration",
  },
]

export function Sidebar({ isCollapsed, onToggle, isMobileOpen, onMobileClose }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onMobileClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          "fixed left-0 top-0 z-50 h-full bg-sidebar border-r border-sidebar-border transition-all duration-300 ease-in-out",
          isCollapsed ? "w-16" : "w-64",
          // Mobile responsive behavior
          "lg:translate-x-0",
          isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
          {!isCollapsed && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center shrink-0">
                <Cloud className="w-5 h-5 text-primary-foreground" />
              </div>
              <div className="min-w-0">
                <h1 className="text-sm font-semibold text-sidebar-foreground truncate">SmartCloudOps</h1>
                <p className="text-xs text-muted-foreground truncate">AI Intelligence</p>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            {/* Mobile Close Button */}
            {isMobileOpen && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onMobileClose}
                className="lg:hidden w-8 h-8 p-0 enterprise-focus"
                aria-label="Close navigation menu"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
            
            {/* Collapse Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className={cn(
                "p-1.5 rounded-lg hover:bg-sidebar-accent transition-colors enterprise-focus",
                isCollapsed && "mx-auto"
              )}
              aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              <ChevronLeft 
                className={cn(
                  "w-4 h-4 text-muted-foreground transition-transform duration-200", 
                  isCollapsed && "rotate-180"
                )} 
              />
            </Button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-2 space-y-1 overflow-y-auto h-[calc(100vh-8rem)]">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 enterprise-focus",
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                  isCollapsed && "justify-center",
                )}
                title={isCollapsed ? item.name : undefined}
                aria-current={isActive ? "page" : undefined}
                onClick={onMobileClose} // Close mobile menu on navigation
              >
                <Icon 
                  className={cn(
                    "w-5 h-5 shrink-0", 
                    isActive ? "text-primary" : "text-muted-foreground"
                  )} 
                />
                {!isCollapsed && (
                  <div className="flex-1 min-w-0">
                    <div className="truncate">{item.name}</div>
                    <div className="text-xs text-muted-foreground truncate">{item.description}</div>
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        {!isCollapsed && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-sidebar-accent/50 rounded-lg p-3 border border-sidebar-border">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" aria-hidden="true" />
                <span className="text-xs font-medium text-sidebar-foreground">System Status</span>
              </div>
              <p className="text-xs text-muted-foreground">All systems operational</p>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
