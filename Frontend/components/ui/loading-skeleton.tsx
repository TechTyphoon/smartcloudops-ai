"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export function MetricsGridSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={i} className="animate-pulse">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="h-4 bg-muted rounded w-24"></div>
            <div className="h-4 w-4 bg-muted rounded"></div>
          </CardHeader>
          <CardContent>
            <div className="h-8 bg-muted rounded w-16 mb-2"></div>
            <div className="h-3 bg-muted rounded w-32"></div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export function TableSkeleton({ columns = 6, rows = 5 }: { columns?: number; rows?: number }) {
  return (
    <Card>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              {Array.from({ length: columns }).map((_, i) => (
                <TableHead key={i}>
                  <div className="h-4 bg-muted rounded w-20 animate-pulse"></div>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.from({ length: rows }).map((_, rowIndex) => (
              <TableRow key={rowIndex}>
                {Array.from({ length: columns }).map((_, colIndex) => (
                  <TableCell key={colIndex}>
                    <div className="h-4 bg-muted rounded w-16 animate-pulse"></div>
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export function StatsSkeleton() {
  return (
    <div className="space-y-4">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between">
        <div className="h-6 bg-muted rounded w-32 animate-pulse"></div>
        <div className="flex gap-2">
          <div className="h-9 bg-muted rounded w-24 animate-pulse"></div>
          <div className="h-9 bg-muted rounded w-32 animate-pulse"></div>
        </div>
      </div>
      
      {/* Metrics Grid Skeleton */}
      <MetricsGridSkeleton />
      
      {/* Additional Cards Skeleton */}
      <div className="grid gap-4 md:grid-cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-5 bg-muted rounded w-40"></div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <div className="h-4 bg-muted rounded w-24"></div>
                  <div className="h-4 bg-muted rounded w-12"></div>
                </div>
                <div className="h-2 bg-muted rounded"></div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <div className="h-4 bg-muted rounded w-20"></div>
                  <div className="h-4 bg-muted rounded w-16"></div>
                </div>
                <div className="h-2 bg-muted rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export function PanelHeaderSkeleton() {
  return (
    <div className="flex items-center justify-between animate-pulse">
      <div className="flex items-center gap-4">
        <div className="h-6 bg-muted rounded w-32"></div>
        <div className="h-8 bg-muted rounded w-24"></div>
      </div>
      <div className="h-9 bg-muted rounded w-32"></div>
    </div>
  )
}

export function FormSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div>
        <div className="h-4 bg-muted rounded w-16 mb-2"></div>
        <div className="h-9 bg-muted rounded"></div>
      </div>
      <div>
        <div className="h-4 bg-muted rounded w-20 mb-2"></div>
        <div className="h-20 bg-muted rounded"></div>
      </div>
      <div>
        <div className="h-4 bg-muted rounded w-24 mb-2"></div>
        <div className="h-9 bg-muted rounded"></div>
      </div>
      <div className="flex justify-end gap-2">
        <div className="h-9 bg-muted rounded w-16"></div>
        <div className="h-9 bg-muted rounded w-20"></div>
      </div>
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <Card className="animate-pulse">
      <CardHeader>
        <div className="h-5 bg-muted rounded w-40"></div>
      </CardHeader>
      <CardContent>
        <div className="h-64 bg-muted rounded"></div>
      </CardContent>
    </Card>
  )
}

export function QualityReportSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Overall Score Skeleton */}
      <div className="text-center">
        <div className="h-10 bg-muted rounded w-20 mx-auto mb-2"></div>
        <div className="h-6 bg-muted rounded w-16 mx-auto"></div>
      </div>

      {/* Quality Dimensions Skeleton */}
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="flex justify-between">
              <div className="h-4 bg-muted rounded w-20"></div>
              <div className="h-4 bg-muted rounded w-12"></div>
            </div>
            <div className="h-2 bg-muted rounded"></div>
          </div>
        ))}
      </div>

      {/* Issues and Recommendations Skeleton */}
      <div className="space-y-4">
        <div>
          <div className="h-5 bg-muted rounded w-24 mb-2"></div>
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="w-3 h-3 bg-muted rounded-full"></div>
                <div className="h-4 bg-muted rounded flex-1"></div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="h-5 bg-muted rounded w-32 mb-2"></div>
          <div className="space-y-2">
            {Array.from({ length: 2 }).map((_, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="w-3 h-3 bg-muted rounded-full"></div>
                <div className="h-4 bg-muted rounded flex-1"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
