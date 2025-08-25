"use client"

import type React from "react"

import { createContext, useContext, useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"

interface User {
  email: string
  name: string
  role: string
}

interface AuthContextType {
  user: User | null
  login: (user: User) => Promise<void>
  logout: () => void
  isLoading: boolean
  validateSession: () => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const SESSION_TIMEOUT = 30 * 60 * 1000

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const validateSession = useCallback((): boolean => {
    const storedUser = localStorage.getItem("smartcloudops-user")
    const sessionTimestamp = localStorage.getItem("smartcloudops-session-timestamp")

    if (!storedUser || !sessionTimestamp) {
      return false
    }

    const now = Date.now()
    const sessionTime = Number.parseInt(sessionTimestamp, 10)

    // Check if session has expired
    if (now - sessionTime > SESSION_TIMEOUT) {
      localStorage.removeItem("smartcloudops-user")
      localStorage.removeItem("smartcloudops-session-timestamp")
      return false
    }

    return true
  }, [])

  useEffect(() => {
    const storedUser = localStorage.getItem("smartcloudops-user")
    if (storedUser && validateSession()) {
      try {
        const userData = JSON.parse(storedUser)
        if (userData.email && userData.name && userData.role) {
          setUser(userData)
          localStorage.setItem("smartcloudops-session-timestamp", Date.now().toString())
        } else {
          localStorage.removeItem("smartcloudops-user")
          localStorage.removeItem("smartcloudops-session-timestamp")
        }
      } catch (error) {
        console.warn("Failed to parse stored user data:", error)
        localStorage.removeItem("smartcloudops-user")
        localStorage.removeItem("smartcloudops-session-timestamp")
      }
    }
    setIsLoading(false)
  }, [validateSession])

  useEffect(() => {
    const interval = setInterval(
      () => {
        if (user && !validateSession()) {
          setUser(null)
          router.push("/login")
        }
      },
      5 * 60 * 1000,
    ) // Check every 5 minutes

    return () => clearInterval(interval)
  }, [user, validateSession, router])

  const login = async (userData: User) => {
    if (!userData.email || !userData.name || !userData.role) {
      throw new Error("Invalid user data: missing required fields")
    }

    setUser(userData)
    localStorage.setItem("smartcloudops-user", JSON.stringify(userData))
    localStorage.setItem("smartcloudops-session-timestamp", Date.now().toString())
  }

  const logout = useCallback(() => {
    setUser(null)
    localStorage.removeItem("smartcloudops-user")
    localStorage.removeItem("smartcloudops-session-timestamp")
    router.push("/login")
  }, [router])

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading, validateSession }}>{children}</AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
