"use client"

import React from "react"
import { cn } from "@/lib/utils"

interface ResponsiveContainerProps {
  children: React.ReactNode
  className?: string
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full"
  padding?: "none" | "sm" | "md" | "lg" | "xl"
  center?: boolean
}

const maxWidthClasses = {
  sm: "max-w-sm",
  md: "max-w-md", 
  lg: "max-w-lg",
  xl: "max-w-xl",
  "2xl": "max-w-2xl",
  full: "max-w-full"
}

const paddingClasses = {
  none: "",
  sm: "px-2 sm:px-4",
  md: "px-4 sm:px-6",
  lg: "px-4 sm:px-6 lg:px-8",
  xl: "px-4 sm:px-6 lg:px-8 xl:px-12"
}

export function ResponsiveContainer({
  children,
  className,
  maxWidth = "full",
  padding = "md",
  center = false
}: ResponsiveContainerProps) {
  return (
    <div 
      className={cn(
        "w-full",
        maxWidthClasses[maxWidth],
        paddingClasses[padding],
        center && "mx-auto",
        className
      )}
    >
      {children}
    </div>
  )
}

// Responsive Grid Component
interface ResponsiveGridProps {
  children: React.ReactNode
  className?: string
  cols?: {
    default?: number
    sm?: number
    md?: number
    lg?: number
    xl?: number
    "2xl"?: number
  }
  gap?: "sm" | "md" | "lg" | "xl"
}

const gapClasses = {
  sm: "gap-2",
  md: "gap-4", 
  lg: "gap-6",
  xl: "gap-8"
}

export function ResponsiveGrid({
  children,
  className,
  cols = { default: 1, md: 2, lg: 3 },
  gap = "md"
}: ResponsiveGridProps) {
  const gridClasses = Object.entries(cols)
    .map(([breakpoint, colCount]) => {
      if (breakpoint === "default") {
        return `grid-cols-${colCount}`
      }
      return `${breakpoint}:grid-cols-${colCount}`
    })
    .join(" ")

  return (
    <div 
      className={cn(
        "grid",
        gridClasses,
        gapClasses[gap],
        className
      )}
    >
      {children}
    </div>
  )
}

// Responsive Stack Component  
interface ResponsiveStackProps {
  children: React.ReactNode
  className?: string
  direction?: {
    default?: "row" | "col"
    sm?: "row" | "col"
    md?: "row" | "col"
    lg?: "row" | "col"
    xl?: "row" | "col"
  }
  gap?: "sm" | "md" | "lg" | "xl"
  align?: "start" | "center" | "end" | "stretch"
  justify?: "start" | "center" | "end" | "between" | "around" | "evenly"
}

const alignClasses = {
  start: "items-start",
  center: "items-center", 
  end: "items-end",
  stretch: "items-stretch"
}

const justifyClasses = {
  start: "justify-start",
  center: "justify-center",
  end: "justify-end", 
  between: "justify-between",
  around: "justify-around",
  evenly: "justify-evenly"
}

export function ResponsiveStack({
  children,
  className,
  direction = { default: "col", md: "row" },
  gap = "md",
  align = "start",
  justify = "start"
}: ResponsiveStackProps) {
  const directionClasses = Object.entries(direction)
    .map(([breakpoint, dir]) => {
      const flexClass = dir === "row" ? "flex-row" : "flex-col"
      if (breakpoint === "default") {
        return flexClass
      }
      return `${breakpoint}:${flexClass}`
    })
    .join(" ")

  return (
    <div 
      className={cn(
        "flex",
        directionClasses,
        gapClasses[gap],
        alignClasses[align],
        justifyClasses[justify],
        className
      )}
    >
      {children}
    </div>
  )
}

// Responsive Show/Hide Components
interface ResponsiveShowProps {
  children: React.ReactNode
  above?: "sm" | "md" | "lg" | "xl" | "2xl"
  below?: "sm" | "md" | "lg" | "xl" | "2xl"
  only?: "sm" | "md" | "lg" | "xl" | "2xl"
}

export function ResponsiveShow({ children, above, below, only }: ResponsiveShowProps) {
  let className = ""
  
  if (only) {
    // Hide by default, show only at specific breakpoint
    className = "hidden"
    if (only === "sm") className += " sm:block md:hidden"
    else if (only === "md") className += " md:block lg:hidden" 
    else if (only === "lg") className += " lg:block xl:hidden"
    else if (only === "xl") className += " xl:block 2xl:hidden"
    else if (only === "2xl") className += " 2xl:block"
  } else if (above) {
    // Hide by default, show above breakpoint
    className = `hidden ${above}:block`
  } else if (below) {
    // Show by default, hide above breakpoint  
    className = `block ${below}:hidden`
  }

  return <div className={className}>{children}</div>
}

export function ResponsiveHide({ children, above, below, only }: ResponsiveShowProps) {
  let className = ""
  
  if (only) {
    // Show by default, hide only at specific breakpoint
    className = "block"
    if (only === "sm") className += " sm:hidden md:block"
    else if (only === "md") className += " md:hidden"
    else if (only === "lg") className += " lg:hidden" 
    else if (only === "xl") className += " xl:hidden"
    else if (only === "2xl") className += " 2xl:hidden"
  } else if (above) {
    // Show by default, hide above breakpoint
    className = `block ${above}:hidden`
  } else if (below) {
    // Hide by default, show above breakpoint
    className = `hidden ${below}:block`
  }

  return <div className={className}>{children}</div>
}
