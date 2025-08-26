/**
 * Tests for MLOps Overview Component
 * Phase 2B Week 3: UI Polish & Testing
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { render, mockAPIResponses, createMockMLOpsStore } from '@/__tests__/utils/test-utils'
import { MLOpsOverview } from '@/components/mlops/mlops-overview'

// Mock the MLOps store hooks
const mockStore = createMockMLOpsStore()
vi.mock('@/lib/stores/mlops-store', () => ({
  useMLOpsStats: () => ({
    statistics: mockStore.statistics,
    loading: mockStore.statisticsLoading,
    error: mockStore.statisticsError,
    fetch: mockStore.fetchStatistics,
  }),
  useRealTime: () => ({
    enabled: mockStore.realTimeEnabled,
    start: mockStore.startRealTimeUpdates,
    stop: mockStore.stopRealTimeUpdates,
  }),
}))

describe('MLOpsOverview', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Loading State', () => {
    it('displays loading skeleton when data is loading', () => {
      mockStore.statisticsLoading = true
      render(<MLOpsOverview />)
      
      // Check for loading skeleton elements
      expect(screen.getByText('MLOps Overview')).toBeInTheDocument()
      expect(screen.getAllByRole('generic')).toBeTruthy() // Skeleton divs
    })
  })

  describe('Error State', () => {
    it('displays error message when statistics fetch fails', () => {
      mockStore.statisticsLoading = false
      mockStore.statisticsError = 'Failed to fetch statistics'
      
      render(<MLOpsOverview />)
      
      expect(screen.getByText('Failed to fetch statistics')).toBeInTheDocument()
      expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument() // AlertTriangle icon
    })

    it('displays service unavailable message for MLOps service error', () => {
      mockStore.statisticsLoading = false
      mockStore.statisticsError = 'MLOps service unavailable'
      
      render(<MLOpsOverview />)
      
      expect(screen.getByText('MLOps service is starting up. Please wait a moment...')).toBeInTheDocument()
    })
  })

  describe('Success State', () => {
    beforeEach(() => {
      mockStore.statisticsLoading = false
      mockStore.statisticsError = null
      mockStore.statistics = mockAPIResponses.statistics.success.data
    })

    it('displays all key metrics cards', () => {
      render(<MLOpsOverview />)
      
      expect(screen.getByText('Total Experiments')).toBeInTheDocument()
      expect(screen.getByText('Registered Models')).toBeInTheDocument()
      expect(screen.getByText('Data Versions')).toBeInTheDocument()
      expect(screen.getByText('Datasets')).toBeInTheDocument()
    })

    it('displays correct statistics values', () => {
      render(<MLOpsOverview />)
      
      // Check experiment stats
      expect(screen.getByText('5')).toBeInTheDocument() // Total experiments
      expect(screen.getByText('2 active, 3 completed')).toBeInTheDocument()
      
      // Check model stats
      expect(screen.getByText('3')).toBeInTheDocument() // Total models
      expect(screen.getByText('1 in production')).toBeInTheDocument()
      
      // Check data pipeline stats
      expect(screen.getByText('8')).toBeInTheDocument() // Total versions
      expect(screen.getByText('Avg. quality: 87.0%')).toBeInTheDocument()
      
      expect(screen.getByText('2')).toBeInTheDocument() // Total datasets
    })

    it('displays detailed status cards', () => {
      render(<MLOpsOverview />)
      
      expect(screen.getByText('Experiment Status')).toBeInTheDocument()
      expect(screen.getByText('Model Deployment')).toBeInTheDocument()
      expect(screen.getByText('Data Quality Distribution')).toBeInTheDocument()
    })

    it('shows active experiments badge', () => {
      render(<MLOpsOverview />)
      
      const activeBadge = screen.getByText('2')
      expect(activeBadge.closest('[class*="bg-"]')).toBeInTheDocument()
    })

    it('displays quality status distribution', () => {
      render(<MLOpsOverview />)
      
      expect(screen.getByText('Excellent')).toBeInTheDocument()
      expect(screen.getByText('Good')).toBeInTheDocument()
      expect(screen.getByText('Fair')).toBeInTheDocument()
      expect(screen.getByText('Poor')).toBeInTheDocument()
      expect(screen.getByText('Failed')).toBeInTheDocument()
    })
  })

  describe('Real-time Controls', () => {
    beforeEach(() => {
      mockStore.statisticsLoading = false
      mockStore.statisticsError = null
      mockStore.statistics = mockAPIResponses.statistics.success.data
    })

    it('displays real-time controls in header', () => {
      render(<MLOpsOverview />)
      
      expect(screen.getByText('Refresh')).toBeInTheDocument()
      expect(screen.getByText('Start Live')).toBeInTheDocument()
    })

    it('shows live badge when real-time is enabled', () => {
      mockStore.realTimeEnabled = true
      render(<MLOpsOverview />)
      
      expect(screen.getByText('Live')).toBeInTheDocument()
      expect(screen.getByText('Stop Live')).toBeInTheDocument()
    })

    it('calls refresh function when refresh button is clicked', async () => {
      render(<MLOpsOverview />)
      
      const refreshButton = screen.getByText('Refresh')
      await userEvent.click(refreshButton)
      
      expect(mockStore.fetchStatistics).toHaveBeenCalledWith(true)
    })

    it('toggles real-time updates when live button is clicked', async () => {
      render(<MLOpsOverview />)
      
      const liveButton = screen.getByText('Start Live')
      await userEvent.click(liveButton)
      
      expect(mockStore.startRealTimeUpdates).toHaveBeenCalled()
    })
  })

  describe('Progress Bars', () => {
    beforeEach(() => {
      mockStore.statisticsLoading = false
      mockStore.statisticsError = null
      mockStore.statistics = mockAPIResponses.statistics.success.data
    })

    it('displays progress bars with correct values', () => {
      render(<MLOpsOverview />)
      
      // Find progress elements by their role
      const progressBars = screen.getAllByRole('progressbar')
      expect(progressBars.length).toBeGreaterThan(0)
    })

    it('calculates success rate correctly', () => {
      render(<MLOpsOverview />)
      
      // Success rate should be completed/total = 3/5 = 60%
      expect(screen.getByText('60.0%')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    beforeEach(() => {
      mockStore.statisticsLoading = false
      mockStore.statisticsError = null
      mockStore.statistics = mockAPIResponses.statistics.success.data
    })

    it('has proper ARIA labels for interactive elements', () => {
      render(<MLOpsOverview />)
      
      const refreshButton = screen.getByText('Refresh')
      const liveButton = screen.getByText('Start Live')
      
      expect(refreshButton).toBeInTheDocument()
      expect(liveButton).toBeInTheDocument()
    })

    it('provides meaningful text content for screen readers', () => {
      render(<MLOpsOverview />)
      
      expect(screen.getByText('Total Experiments')).toBeInTheDocument()
      expect(screen.getByText('2 active, 3 completed')).toBeInTheDocument()
    })
  })

  describe('Component Lifecycle', () => {
    it('fetches statistics on mount', () => {
      render(<MLOpsOverview />)
      
      expect(mockStore.fetchStatistics).toHaveBeenCalled()
      expect(mockStore.startRealTimeUpdates).toHaveBeenCalled()
    })

    it('stops real-time updates on unmount', () => {
      const { unmount } = render(<MLOpsOverview />)
      
      unmount()
      
      expect(mockStore.stopRealTimeUpdates).toHaveBeenCalled()
    })
  })
})
