import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Basic health check
    const healthData = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0',
      services: {
        frontend: 'up',
        api: 'unknown', // Will be checked if API_URL is available
      }
    }

    // Check backend API if configured
    const apiUrl = process.env.NEXT_PUBLIC_API_URL
    if (apiUrl) {
      try {
        const apiResponse = await fetch(`${apiUrl}/health`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          // Short timeout for health check
          signal: AbortSignal.timeout(5000),
        })

        if (apiResponse.ok) {
          healthData.services.api = 'up'
        } else {
          healthData.services.api = 'down'
        }
      } catch (error) {
        healthData.services.api = 'down'
        console.warn('Backend API health check failed:', error)
      }
    }

    return NextResponse.json(healthData, { status: 200 })
  } catch (error) {
    console.error('Health check failed:', error)
    
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: 'Health check failed',
      },
      { status: 500 }
    )
  }
}
