"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { MessageSquare, Activity, AlertTriangle, Wrench, Settings, ChevronLeft, Cloud } from "lucide-react"
import { cn } from "@/lib/utils"

interface SidebarProps {
  isCollapsed: boolean
  onToggle: () => void
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

export function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  const pathname = usePathname()

  return (
    <div
      className={cn(
        "fixed left-0 top-0 z-40 h-full bg-slate-900 border-r border-slate-800 transition-all duration-300 ease-in-out",
        isCollapsed ? "w-16" : "w-64",
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-teal-400 to-blue-500 rounded-lg flex items-center justify-center">
              <Cloud className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-white">SmartCloudOps</h1>
              <p className="text-xs text-slate-400">AI Intelligence</p>
            </div>
          </div>
        )}
        <button
          onClick={onToggle}
          className={cn("p-1.5 rounded-lg hover:bg-slate-800 transition-colors", isCollapsed && "mx-auto")}
        >
          <ChevronLeft className={cn("w-4 h-4 text-slate-400 transition-transform", isCollapsed && "rotate-180")} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-2 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-teal-500/10 text-teal-400 border border-teal-500/20"
                  : "text-slate-300 hover:text-white hover:bg-slate-800",
                isCollapsed && "justify-center",
              )}
              title={isCollapsed ? item.name : undefined}
            >
              <Icon className={cn("w-5 h-5 flex-shrink-0", isActive ? "text-teal-400" : "text-slate-400")} />
              {!isCollapsed && (
                <div className="flex-1 min-w-0">
                  <div className="truncate">{item.name}</div>
                  <div className="text-xs text-slate-500 truncate">{item.description}</div>
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs font-medium text-slate-300">System Status</span>
            </div>
            <p className="text-xs text-slate-400">All systems operational</p>
          </div>
        </div>
      )}
    </div>
  )
}
