"use client"

import { Bell, Search, User, Moon, Sun, LogOut, Menu } from "lucide-react"
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
import { useState } from "react"

interface HeaderProps {
  onMobileMenuToggle?: () => void
}

export function Header({ onMobileMenuToggle }: HeaderProps) {
  const { theme, setTheme } = useTheme()
  const { user, logout } = useAuth()
  const [searchValue, setSearchValue] = useState("")

  const handleThemeToggle = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // Implement search functionality
    console.log("Searching for:", searchValue)
  }

  return (
    <header className="sticky top-0 z-50 h-16 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
      <div className="flex items-center justify-between h-full px-4 sm:px-6 lg:px-8">
        {/* Mobile Menu Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onMobileMenuToggle}
          className="lg:hidden w-9 h-9 p-0"
          aria-label="Toggle mobile navigation menu"
        >
          <Menu className="h-4 w-4" />
        </Button>

        {/* Search - Responsive Design */}
        <div className="flex-1 max-w-md mx-4 lg:mx-6">
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <input
              type="text"
              placeholder="Search SmartCloudOps..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm bg-muted/50 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all duration-200"
            />
          </form>
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleThemeToggle}
            className="w-9 h-9 p-0"
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>

          {/* Notifications */}
          <Button
            variant="ghost"
            size="sm"
            className="w-9 h-9 p-0 relative"
            aria-label="View notifications (1 unread)"
            aria-describedby="notification-count"
          >
            <Bell className="w-4 h-4" />
            <span
              id="notification-count"
              className="absolute -top-1 -right-1 w-2 h-2 bg-destructive rounded-full animate-pulse"
              aria-label="1 unread notification"
            />
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="w-9 h-9 p-0"
                aria-label={`User menu for ${user?.name || "user"}`}
                aria-expanded="false"
              >
                <User className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56" sideOffset={8}>
              <div className="px-2 py-1.5 text-sm text-muted-foreground">
                <div className="font-medium text-foreground truncate">
                  {user?.name || "Unknown User"}
                </div>
                <div className="text-xs truncate">
                  {user?.email || "No email"}
                </div>
                <div className="text-xs capitalize text-primary">
                  {user?.role || "user"}
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer">
                <User className="mr-2 h-4 w-4" />
                Profile Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={logout}
                className="text-destructive focus:text-destructive cursor-pointer"
                aria-label="Sign out of SmartCloudOps AI"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
