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
      {/* Mobile overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onMobileClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          "fixed top-0 left-0 z-50 h-full bg-sidebar border-r border-sidebar-border transition-all duration-300 ease-in-out",
          "flex flex-col",
          // Desktop: always visible, collapsible
          "lg:relative lg:z-auto",
          // Mobile: slide in/out
          isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
          // Width based on collapsed state
          isCollapsed ? "w-16" : "w-64"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
          {!isCollapsed && (
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                <Cloud className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <h1 className="text-lg font-bold text-sidebar-foreground truncate">
                  SmartCloudOps
                </h1>
                <p className="text-xs text-muted-foreground truncate">AI Platform</p>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            {/* Mobile close button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onMobileClose}
              className="lg:hidden h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
            
            {/* Desktop collapse button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className="hidden lg:flex h-8 w-8 p-0"
            >
              <ChevronLeft className={cn(
                "h-4 w-4 transition-transform duration-200",
                isCollapsed && "rotate-180"
              )} />
            </Button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                  "hover:bg-sidebar-accent hover:text-sidebar-foreground",
                  "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-sidebar",
                  
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/20 shadow-sm"
                    : "text-muted-foreground",

                  isCollapsed && "justify-center px-2",
                )}
                title={isCollapsed ? item.name : undefined}
                aria-current={isActive ? "page" : undefined}
                onClick={onMobileClose}
              >
                <Icon 
                  className={cn(
                    "w-5 h-5 shrink-0", 
                    isActive ? "text-primary" : "text-muted-foreground"
                  )} 
                />
                {!isCollapsed && (
                  <div className="flex-1 min-w-0">
                    <div className="truncate font-medium">{item.name}</div>
                    <div className="text-xs text-muted-foreground truncate mt-0.5">{item.description}</div>
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        {!isCollapsed && (
          <div className="p-4 border-t border-sidebar-border">
            <div className="bg-sidebar-accent/50 rounded-lg p-4 border border-sidebar-border">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" aria-hidden="true" />
                <span className="text-sm font-medium text-sidebar-foreground">System Status</span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                All systems operational
              </p>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
