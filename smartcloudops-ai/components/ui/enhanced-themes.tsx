"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"
import { designTokens } from "@/lib/design-system/tokens"

// Enhanced theme configuration
const themes = {
  light: {
    name: 'light',
    colors: {
      primary: designTokens.colors.primary[600],
      secondary: designTokens.colors.gray[100],
      accent: designTokens.colors.mlops.experiment,
      background: designTokens.colors.gray[50],
      foreground: designTokens.colors.gray[900],
      muted: designTokens.colors.gray[100],
      mutedForeground: designTokens.colors.gray[600],
      border: designTokens.colors.gray[200],
      card: '#ffffff',
      popover: '#ffffff',
    },
    shadows: designTokens.boxShadow,
    borderRadius: designTokens.borderRadius,
  },
  dark: {
    name: 'dark',
    colors: {
      primary: designTokens.colors.primary[400],
      secondary: designTokens.colors.gray[800],
      accent: designTokens.colors.mlops.experiment,
      background: designTokens.colors.gray[900],
      foreground: designTokens.colors.gray[100],
      muted: designTokens.colors.gray[800],
      mutedForeground: designTokens.colors.gray[400],
      border: designTokens.colors.gray[700],
      card: designTokens.colors.gray[800],
      popover: designTokens.colors.gray[800],
    },
    shadows: designTokens.boxShadow,
    borderRadius: designTokens.borderRadius,
  },
  'high-contrast': {
    name: 'high-contrast',
    colors: {
      primary: '#000000',
      secondary: '#ffffff',
      accent: '#ffff00',
      background: '#ffffff',
      foreground: '#000000',
      muted: '#f0f0f0',
      mutedForeground: '#666666',
      border: '#000000',
      card: '#ffffff',
      popover: '#ffffff',
    },
    shadows: designTokens.boxShadow,
    borderRadius: designTokens.borderRadius,
  },
} as const

// Context for theme configuration
interface ThemeContextType {
  currentTheme: keyof typeof themes
  themeConfig: typeof themes.light
  updateTheme: (theme: keyof typeof themes) => void
  toggleHighContrast: () => void
  isHighContrast: boolean
}

const ThemeContext = React.createContext<ThemeContextType | undefined>(undefined)

export function useThemeConfig() {
  const context = React.useContext(ThemeContext)
  if (!context) {
    throw new Error('useThemeConfig must be used within a ThemeConfigProvider')
  }
  return context
}

interface ThemeConfigProviderProps extends ThemeProviderProps {
  children: React.ReactNode
}

export function ThemeConfigProvider({ children, ...props }: ThemeConfigProviderProps) {
  const [currentTheme, setCurrentTheme] = React.useState<keyof typeof themes>('light')
  const [isHighContrast, setIsHighContrast] = React.useState(false)

  // Get current theme configuration
  const themeConfig = React.useMemo(() => {
    if (isHighContrast) {
      return themes['high-contrast']
    }
    return themes[currentTheme]
  }, [currentTheme, isHighContrast])

  // Update CSS custom properties when theme changes
  React.useEffect(() => {
    const root = document.documentElement
    const colors = themeConfig.colors

    // Set CSS custom properties
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value)
    })

    // Update theme class
    root.classList.remove('light', 'dark', 'high-contrast')
    root.classList.add(themeConfig.name)
  }, [themeConfig])

  const updateTheme = React.useCallback((theme: keyof typeof themes) => {
    setCurrentTheme(theme)
  }, [])

  const toggleHighContrast = React.useCallback(() => {
    setIsHighContrast(prev => !prev)
  }, [])

  const contextValue = React.useMemo(() => ({
    currentTheme,
    themeConfig,
    updateTheme,
    toggleHighContrast,
    isHighContrast,
  }), [currentTheme, themeConfig, updateTheme, toggleHighContrast, isHighContrast])

  return (
    <ThemeContext.Provider value={contextValue}>
      <NextThemesProvider {...props}>
        {children}
      </NextThemesProvider>
    </ThemeContext.Provider>
  )
}

// Enhanced theme toggle component
export function ThemeToggle() {
  const { currentTheme, updateTheme, toggleHighContrast, isHighContrast } = useThemeConfig()

  return (
    <div className="flex items-center gap-2">
      <select 
        value={currentTheme}
        onChange={(e) => updateTheme(e.target.value as keyof typeof themes)}
        className="px-2 py-1 rounded border text-sm"
        aria-label="Select theme"
      >
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
      
      <button
        onClick={toggleHighContrast}
        className={`px-2 py-1 rounded text-sm border ${
          isHighContrast 
            ? 'bg-yellow-500 text-black border-black' 
            : 'bg-transparent border-gray-300'
        }`}
        aria-label={`${isHighContrast ? 'Disable' : 'Enable'} high contrast mode`}
        aria-pressed={isHighContrast}
      >
        High Contrast
      </button>
    </div>
  )
}
