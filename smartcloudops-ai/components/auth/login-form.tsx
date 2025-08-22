"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, Lock, Mail } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"

const DEMO_CREDENTIALS = {
  email: "admin@smartcloudops.ai",
  password: "demo123",
}

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      if (!email || !email.includes("@")) {
        throw new Error("Please enter a valid email address")
      }

      if (!password || password.length < 3) {
        throw new Error("Password must be at least 3 characters long")
      }

      if (email.trim() === DEMO_CREDENTIALS.email && password === DEMO_CREDENTIALS.password) {
        await login({
          email: email.trim(),
          name: "System Administrator",
          role: "admin",
        })
        router.push("/")
      } else {
        setError("Invalid credentials. Use admin@smartcloudops.ai / demo123 for demo access.")
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Authentication failed. Please try again."
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert className="border-red-500/50 bg-red-500/10">
          <AlertDescription className="text-red-400">{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="email" className="text-slate-200">
          Email Address
        </Label>
        <div className="relative">
          <Mail className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="pl-10 bg-slate-800/50 border-slate-600 text-white"
            placeholder="admin@smartcloudops.ai"
            required
            autoComplete="email"
            aria-describedby="email-error"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="password" className="text-slate-200">
          Password
        </Label>
        <div className="relative">
          <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pl-10 bg-slate-800/50 border-slate-600 text-white"
            placeholder="demo123"
            required
            autoComplete="current-password"
            aria-describedby="password-error"
          />
        </div>
      </div>

      <Button
        type="submit"
        className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 enterprise-focus"
        disabled={isLoading}
        aria-label={isLoading ? "Authenticating user" : "Sign in to SmartCloudOps AI"}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Authenticating...
          </>
        ) : (
          "Sign In to SmartCloudOps AI"
        )}
      </Button>
    </form>
  )
}
