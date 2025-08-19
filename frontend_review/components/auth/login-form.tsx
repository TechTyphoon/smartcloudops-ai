"use client"

import type React from "react"
import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, Lock, Mail, Eye, EyeOff } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import { cn } from "@/lib/utils"

const DEMO_CREDENTIALS = {
  email: "admin@smartcloudops.ai",
  password: "demo123",
}

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [emailError, setEmailError] = useState("")
  const [passwordError, setPasswordError] = useState("")
  
  const { login } = useAuth()
  const router = useRouter()

  const validateEmail = useCallback((email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email) {
      setEmailError("Email is required")
      return false
    }
    if (!emailRegex.test(email)) {
      setEmailError("Please enter a valid email address")
      return false
    }
    setEmailError("")
    return true
  }, [])

  const validatePassword = useCallback((password: string): boolean => {
    if (!password) {
      setPasswordError("Password is required")
      return false
    }
    if (password.length < 3) {
      setPasswordError("Password must be at least 3 characters long")
      return false
    }
    setPasswordError("")
    return true
  }, [])

  const handleEmailChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setEmail(value)
    if (emailError) {
      validateEmail(value)
    }
  }, [emailError, validateEmail])

  const handlePasswordChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword(value)
    if (passwordError) {
      validatePassword(value)
    }
  }, [passwordError, validatePassword])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    // Validate inputs
    const isEmailValid = validateEmail(email)
    const isPasswordValid = validatePassword(password)

    if (!isEmailValid || !isPasswordValid) {
      setIsLoading(false)
      return
    }

    try {
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
  }, [email, password, validateEmail, validatePassword, login, router])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleSubmit(e)
    }
  }, [handleSubmit])

  const togglePasswordVisibility = useCallback(() => {
    setShowPassword(!showPassword)
  }, [showPassword])

  return (
    <form 
      onSubmit={handleSubmit} 
      className="space-y-6 w-full max-w-md mx-auto"
      noValidate
      aria-labelledby="login-form-title"
    >
      <div className="text-center space-y-2">
        <h1 id="login-form-title" className="text-2xl font-bold tracking-tight">
          Welcome to SmartCloudOps AI
        </h1>
        <p className="text-muted-foreground text-sm">
          Sign in to access your enterprise cloud operations dashboard
        </p>
      </div>

      {error && (
        <Alert className="border-destructive/50 bg-destructive/10" role="alert">
          <AlertDescription className="text-destructive">{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email" className="text-sm font-medium">
            Email Address
          </Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              id="email"
              type="email"
              value={email}
              onChange={handleEmailChange}
              onBlur={() => validateEmail(email)}
              onKeyDown={handleKeyDown}
              className={cn(
                "pl-10 transition-all duration-200",
                emailError && "border-destructive focus-visible:ring-destructive"
              )}
              placeholder="admin@smartcloudops.ai"
              required
              autoComplete="email"
              autoFocus
              aria-describedby={emailError ? "email-error" : "email-help"}
              aria-invalid={!!emailError}
              disabled={isLoading}
            />
          </div>
          {emailError && (
            <p id="email-error" className="text-sm text-destructive" role="alert">
              {emailError}
            </p>
          )}
          <p id="email-help" className="sr-only">
            Enter your email address to sign in
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="password" className="text-sm font-medium">
            Password
          </Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={handlePasswordChange}
              onBlur={() => validatePassword(password)}
              onKeyDown={handleKeyDown}
              className={cn(
                "pl-10 pr-10 transition-all duration-200",
                passwordError && "border-destructive focus-visible:ring-destructive"
              )}
              placeholder="demo123"
              required
              autoComplete="current-password"
              aria-describedby={passwordError ? "password-error" : "password-help"}
              aria-invalid={!!passwordError}
              disabled={isLoading}
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={togglePasswordVisibility}
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0 hover:bg-muted/50"
              aria-label={showPassword ? "Hide password" : "Show password"}
              disabled={isLoading}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          </div>
          {passwordError && (
            <p id="password-error" className="text-sm text-destructive" role="alert">
              {passwordError}
            </p>
          )}
          <p id="password-help" className="sr-only">
            Enter your password to sign in
          </p>
        </div>
      </div>

      <Button
        type="submit"
        className="w-full bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 enterprise-focus"
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

      <div className="text-center">
        <p className="text-xs text-muted-foreground">
          Demo credentials: admin@smartcloudops.ai / demo123
        </p>
      </div>
    </form>
  )
}
