"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { cn } from "@/lib/utils"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Handle responsive behavior
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024) // lg breakpoint
      if (window.innerWidth >= 1024) {
        setIsMobileOpen(false)
      }
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const handleMobileMenuToggle = () => {
    setIsMobileOpen(!isMobileOpen)
  }

  const handleMobileClose = () => {
    setIsMobileOpen(false)
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar 
        isCollapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        isMobileOpen={isMobileOpen}
        onMobileClose={handleMobileClose}
      />

      <div 
        className={cn(
          "transition-all duration-300 ease-in-out",
          // Desktop layout
          "lg:ml-16 lg:ml-64",
          sidebarCollapsed ? "lg:ml-16" : "lg:ml-64",
          // Mobile layout - no margin when sidebar is hidden
          "ml-0"
        )}
      >
        <Header onMobileMenuToggle={handleMobileMenuToggle} />

        <main className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-[1920px] mx-auto">
          {/* Responsive container for ultra-wide screens */}
          <div className="w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
