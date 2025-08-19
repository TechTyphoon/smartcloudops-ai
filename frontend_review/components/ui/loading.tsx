import { Loader2, Loader } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingProps {
  size?: "sm" | "md" | "lg" | "xl"
  variant?: "spinner" | "dots" | "pulse" | "skeleton"
  className?: string
  text?: string
  fullScreen?: boolean
}

export function Loading({ 
  size = "md", 
  variant = "spinner", 
  className,
  text,
  fullScreen = false 
}: LoadingProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8",
    xl: "w-12 h-12"
  }

  const renderSpinner = () => (
    <Loader2 className={cn("animate-spin", sizeClasses[size])} />
  )

  const renderDots = () => (
    <div className="flex space-x-1">
      <div className={cn("w-2 h-2 bg-current rounded-full animate-bounce", sizeClasses[size])} />
      <div 
        className={cn("w-2 h-2 bg-current rounded-full animate-bounce", sizeClasses[size])}
        style={{ animationDelay: "0.1s" }}
      />
      <div 
        className={cn("w-2 h-2 bg-current rounded-full animate-bounce", sizeClasses[size])}
        style={{ animationDelay: "0.2s" }}
      />
    </div>
  )

  const renderPulse = () => (
    <div className={cn("animate-pulse bg-current rounded-full", sizeClasses[size])} />
  )

  const renderSkeleton = () => (
    <div className="space-y-3">
      <div className="animate-pulse bg-muted rounded h-4 w-3/4" />
      <div className="animate-pulse bg-muted rounded h-4 w-1/2" />
      <div className="animate-pulse bg-muted rounded h-4 w-5/6" />
    </div>
  )

  const renderContent = () => {
    switch (variant) {
      case "dots":
        return renderDots()
      case "pulse":
        return renderPulse()
      case "skeleton":
        return renderSkeleton()
      default:
        return renderSpinner()
    }
  }

  const content = (
    <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
      {renderContent()}
      {text && (
        <p className="text-sm text-muted-foreground animate-pulse">
          {text}
        </p>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
        {content}
      </div>
    )
  }

  return content
}

// Skeleton components for content loading
interface SkeletonProps {
  className?: string
  width?: string
  height?: string
  lines?: number
}

export function Skeleton({ className, width, height, lines = 1 }: SkeletonProps) {
  if (lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "animate-pulse bg-muted rounded",
              i === lines - 1 ? "w-3/4" : "w-full",
              height || "h-4",
              className
            )}
          />
        ))}
      </div>
    )
  }

  return (
    <div
      className={cn(
        "animate-pulse bg-muted rounded",
        width || "w-full",
        height || "h-4",
        className
      )}
    />
  )
}

// Card skeleton for loading states
export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center space-x-4">
        <Skeleton className="w-12 h-12 rounded-full" />
        <div className="space-y-2 flex-1">
          <Skeleton className="w-3/4" />
          <Skeleton className="w-1/2" />
        </div>
      </div>
      <Skeleton lines={3} />
      <div className="flex space-x-2">
        <Skeleton className="w-20 h-8" />
        <Skeleton className="w-20 h-8" />
      </div>
    </div>
  )
}

// Table skeleton for data loading
export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="w-24 h-4" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton 
              key={colIndex} 
              className={cn(
                "h-4",
                colIndex === 0 ? "w-32" : "w-24"
              )} 
            />
          ))}
        </div>
      ))}
    </div>
  )
}

// Page loading component
export function PageLoading({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <Loading size="lg" text={text} />
    </div>
  )
}

// Inline loading component
export function InlineLoading({ text }: { text?: string }) {
  return (
    <div className="inline-flex items-center gap-2">
      <Loading size="sm" />
      {text && <span className="text-sm text-muted-foreground">{text}</span>}
    </div>
  )
}
