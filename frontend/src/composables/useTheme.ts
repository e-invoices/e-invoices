import { ref } from 'vue'

type Theme = 'light' | 'dark' | 'system'

// Theme state - persisted in localStorage (defined outside for singleton pattern)
const currentTheme = ref<Theme>('light')
const isDark = ref(false)
let initialized = false

// Apply theme to document immediately
const applyTheme = (dark: boolean) => {
  isDark.value = dark
  if (dark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// Get system preference
const getSystemPreference = (): boolean => {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

// Set theme
const setTheme = (theme: Theme) => {
  currentTheme.value = theme
  localStorage.setItem('theme', theme)

  if (theme === 'system') {
    applyTheme(getSystemPreference())
  } else {
    applyTheme(theme === 'dark')
  }
}

// Toggle between light and dark (based on current appearance)
const toggleTheme = () => {
  if (isDark.value) {
    setTheme('light')
  } else {
    setTheme('dark')
  }
}

// Cycle through themes: light -> dark -> system
const cycleTheme = () => {
  if (currentTheme.value === 'light') {
    setTheme('dark')
  } else if (currentTheme.value === 'dark') {
    setTheme('system')
  } else {
    setTheme('light')
  }
}

// Initialize theme
const initTheme = () => {
  if (initialized) return
  initialized = true

  const savedTheme = localStorage.getItem('theme') as Theme | null
  if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
    setTheme(savedTheme)
  } else {
    setTheme('light') // Default to light
  }

  // Listen for system preference changes
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (currentTheme.value === 'system') {
        applyTheme(e.matches)
      }
    })
  }
}

export function useTheme() {
  return {
    currentTheme,
    isDark,
    setTheme,
    toggleTheme,
    cycleTheme,
    initTheme,
  }
}
