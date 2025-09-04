"use client"

import { Bell, Search, User, Moon, Sun, LogOut } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth } from "@/hooks/use-auth"

export function Header() {
  const { theme, setTheme } = useTheme()
  const { user, logout } = useAuth()

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6">
      {/* Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search operations, logs, metrics..."
            className="w-full pl-10 pr-4 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent enterprise-focus"
            aria-label="Search SmartCloudOps operations, logs, and metrics"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-4">
        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="w-9 h-9 p-0 enterprise-focus"
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>

        {/* Notifications */}
        <Button
          variant="ghost"
          size="sm"
          className="w-9 h-9 p-0 relative enterprise-focus"
          aria-label="View notifications (1 unread)"
        >
          <Bell className="w-4 h-4" />
          <span
            className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"
            aria-label="1 unread notification"
          ></span>
        </Button>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="w-9 h-9 p-0 enterprise-focus"
              aria-label={`User menu for ${user?.name || "user"}`}
            >
              <User className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <div className="px-2 py-1.5 text-sm text-muted-foreground">
              <div className="font-medium text-foreground">{user?.name || "Unknown User"}</div>
              <div className="text-xs">{user?.email || "No email"}</div>
              <div className="text-xs capitalize text-primary">{user?.role || "user"}</div>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="enterprise-focus">
              <User className="mr-2 h-4 w-4" />
              Profile Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={logout}
              className="text-red-600 dark:text-red-400 enterprise-focus"
              aria-label="Sign out of SmartCloudOps AI"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
