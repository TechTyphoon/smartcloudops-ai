/**
 * Testing Utilities for MLOps Components
 * Phase 2B Week 3: UI Polish & Testing
 */

import React from 'react'
import { render, RenderOptions, screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/sonner'

// Mock MLOps Store
export const createMockMLOpsStore = () => ({
  experiments: [],
  experimentsLoading: false,
  experimentsError: null,
  models: [],
  modelsLoading: false,
  modelsError: null,
  dataVersions: [],
  dataVersionsLoading: false,
  dataVersionsError: null,
  statistics: {
    experiments: { total: 0, active: 0, completed: 0, failed: 0 },
    models: { total: 0, production: 0, staging: 0, archived: 0 },
    data_pipeline_stats: {
      total_datasets: 0,
      total_versions: 0,
      average_quality_score: 0.85,
      by_quality_status: { excellent: 0, good: 0, fair: 0, poor: 0, failed: 0 }
    }
  },
  statisticsLoading: false,
  statisticsError: null,
  qualityReports: {},
  refreshing: false,
  lastRefresh: null,
  realTimeEnabled: false,
  updateInterval: 30000,
  optimisticUpdates: {},
  // Action mocks
  fetchExperiments: vi.fn(),
  createExperiment: vi.fn(),
  optimisticCreateExperiment: vi.fn(),
  fetchModels: vi.fn(),
  registerModel: vi.fn(),
  updateModelStatus: vi.fn(),
  optimisticUpdateModelStatus: vi.fn(),
  fetchDataVersions: vi.fn(),
  getQualityReport: vi.fn(),
  fetchStatistics: vi.fn(),
  startRealTimeUpdates: vi.fn(),
  stopRealTimeUpdates: vi.fn(),
  setUpdateInterval: vi.fn(),
  refresh: vi.fn(),
  clearErrors: vi.fn(),
  resetOptimisticUpdates: vi.fn(),
})

// Mock API responses
export const mockAPIResponses = {
  experiments: {
    success: {
      status: 'success' as const,
      data: {
        experiments: [
          {
            id: 'exp-1',
            name: 'Test Experiment',
            description: 'A test experiment',
            status: 'active' as const,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            tags: ['test'],
            parameters: { learning_rate: 0.01 },
            metrics: { accuracy: 0.95 },
            artifact_count: 0,
            run_count: 1,
          },
        ],
        pagination: {
          page: 1,
          per_page: 20,
          total: 1,
          pages: 1,
          has_next: false,
          has_prev: false,
        },
      },
      error: null,
    },
    error: {
      status: 'error' as const,
      data: null,
      error: 'Failed to fetch experiments',
    },
  },

  models: {
    success: {
      status: 'success' as const,
      data: {
        models: [
          {
            id: 'model-1',
            name: 'Test Model',
            version: '1.0.0',
            status: 'production' as const,
            framework: 'scikit-learn',
            model_path: '/models/test_model.pkl',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            tags: ['test'],
            metadata: { accuracy: 0.95 },
          },
        ],
        pagination: {
          page: 1,
          per_page: 20,
          total: 1,
          pages: 1,
          has_next: false,
          has_prev: false,
        },
      },
      error: null,
    },
  },

  statistics: {
    success: {
      status: 'success' as const,
      data: {
        experiments: { total: 5, active: 2, completed: 3, failed: 0 },
        models: { total: 3, production: 1, staging: 1, archived: 1 },
        data_pipeline_stats: {
          total_datasets: 2,
          total_versions: 8,
          average_quality_score: 0.87,
          by_quality_status: { excellent: 3, good: 3, fair: 1, poor: 1, failed: 0 }
        }
      },
      error: null,
    },
  },
}

// Test wrapper component
interface TestWrapperProps {
  children: React.ReactNode
  queryClient?: QueryClient
}

const TestWrapper: React.FC<TestWrapperProps> = ({ 
  children, 
  queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}) => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
        {children}
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  )
}

// Custom render function
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & {
    queryClient?: QueryClient
  }
) => {
  const { queryClient, ...renderOptions } = options || {}
  
  return render(ui, {
    wrapper: ({ children }) => (
      <TestWrapper queryClient={queryClient}>
        {children}
      </TestWrapper>
    ),
    ...renderOptions,
  })
}

// User event utilities
export const userEvents = {
  click: async (element: HTMLElement) => {
    await userEvent.click(element)
  },
  type: async (element: HTMLElement, text: string) => {
    await userEvent.type(element, text)
  },
  clear: async (element: HTMLElement) => {
    await userEvent.clear(element)
  },
  selectOption: async (element: HTMLElement, option: string) => {
    await userEvent.selectOptions(element, option)
  },
  upload: async (element: HTMLElement, file: File) => {
    await userEvent.upload(element, file)
  },
}

// Wait utilities
export const waitUtils = {
  forElement: (callback: () => HTMLElement | null, timeout = 5000) => {
    return waitFor(callback, { timeout })
  },
  forElementToBeRemoved: (element: HTMLElement, timeout = 5000) => {
    return waitForElementToBeRemoved(element, { timeout })
  },
  forLoadingToFinish: async (timeout = 5000) => {
    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument()
    }, { timeout })
  },
}

// Assertion helpers
export const assertions = {
  toBeVisible: (element: HTMLElement) => {
    expect(element).toBeVisible()
  },
  toHaveText: (element: HTMLElement, text: string) => {
    expect(element).toHaveTextContent(text)
  },
  toBeDisabled: (element: HTMLElement) => {
    expect(element).toBeDisabled()
  },
  toBeEnabled: (element: HTMLElement) => {
    expect(element).toBeEnabled()
  },
  toHaveClass: (element: HTMLElement, className: string) => {
    expect(element).toHaveClass(className)
  },
  toHaveAttribute: (element: HTMLElement, attr: string, value?: string) => {
    if (value !== undefined) {
      expect(element).toHaveAttribute(attr, value)
    } else {
      expect(element).toHaveAttribute(attr)
    }
  },
}

// Mock data generators
export const generateMockData = {
  experiment: (overrides = {}) => ({
    id: `exp-${Math.random().toString(36).substr(2, 9)}`,
    name: 'Mock Experiment',
    description: 'A mock experiment for testing',
    status: 'active' as const,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    tags: ['mock', 'test'],
    parameters: { learning_rate: 0.01 },
    metrics: { accuracy: 0.95 },
    artifact_count: 0,
    run_count: 1,
    ...overrides,
  }),

  model: (overrides = {}) => ({
    id: `model-${Math.random().toString(36).substr(2, 9)}`,
    name: 'Mock Model',
    version: '1.0.0',
    status: 'staging' as const,
    framework: 'scikit-learn',
    model_path: '/models/mock_model.pkl',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    tags: ['mock', 'test'],
    metadata: { accuracy: 0.95 },
    ...overrides,
  }),

  dataVersion: (overrides = {}) => ({
    id: `version-${Math.random().toString(36).substr(2, 9)}`,
    dataset_name: 'mock_dataset',
    version: '1.0.0',
    status: 'ready' as const,
    created_at: new Date().toISOString(),
    file_path: '/data/mock_dataset.csv',
    size_bytes: 1024000,
    record_count: 10000,
    quality_score: 0.87,
    quality_status: 'good' as const,
    ...overrides,
  }),
}

// Re-export everything
export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
export { customRender as render }
