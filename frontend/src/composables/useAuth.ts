import { ref } from 'vue'
import type {
  User,
  AuthResponse,
  GoogleCredentialResponse,
  GoogleButtonConfig,
  GoogleInitConfig
} from '@/types/auth'
import { authApi } from '@/api/v1/auth'

// Google Client ID - Replace with your actual Google Client ID
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID'

// Current user state
const currentUser = ref<User | null>(null)
const isAuthenticated = ref(false)

// Google SDK loaded state
const isGoogleLoaded = ref(false)

export function useAuth() {
  const handleLoginSuccess = (data: AuthResponse) => {
    currentUser.value = data.user
    isAuthenticated.value = true
    // Store tokens in localStorage
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token)
    }
    // Note: redirect is now handled by the calling page/component
  }

  const handleRegisterSuccess = (data: AuthResponse) => {
    currentUser.value = data.user
    isAuthenticated.value = true
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token)
    }
    // Note: redirect is now handled by the calling page/component
  }

  const logout = () => {
    currentUser.value = null
    isAuthenticated.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('selected_organization_id')
    // Redirect to landing page
    window.location.href = '/'
  }

  // Initialize Google Sign-In
  const initializeGoogle = (buttonId: string, callback: (response: GoogleCredentialResponse) => void) => {
    if (!isGoogleLoaded.value || !window.google) {
      // Silently skip - Google SDK not available
      return
    }

    try {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: callback,
        auto_select: false,
        cancel_on_tap_outside: true,
      })

      const buttonElement = document.getElementById(buttonId)
      if (buttonElement) {
        window.google.accounts.id.renderButton(buttonElement, {
          theme: 'outline',
          size: 'large',
          width: 320,
          text: buttonId.includes('register') ? 'signup_with' : 'signin_with',
          shape: 'rectangular',
          logo_alignment: 'center',
        })
      }
    } catch (error) {
      // Google Sign-In initialization failed - not critical
      console.warn('Google Sign-In initialization failed:', error)
    }
  }

  // Load Google SDK script
  const loadGoogleScript = () => {
    return new Promise<void>((resolve) => {
      if (window.google?.accounts?.id) {
        isGoogleLoaded.value = true
        resolve()
        return
      }

      const existingScript = document.getElementById('google-gsi-script')
      if (existingScript) {
        existingScript.addEventListener('load', () => {
          isGoogleLoaded.value = true
          resolve()
        })
        return
      }

      const script = document.createElement('script')
      script.id = 'google-gsi-script'
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      script.onload = () => {
        isGoogleLoaded.value = true
        resolve()
      }
      script.onerror = () => {
        // Google SDK failed to load - not critical, user can still use email login
        console.warn('Google Sign-In SDK failed to load. Email login still available.')
        resolve() // Don't reject - app should still work
      }
      document.head.appendChild(script)
    })
  }

  // Check for existing session on mount
  const checkSession = async () => {
    const token = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')

    // If we have an access token but no refresh token, it's from old system - clear it
    if (token && !refreshToken) {
      localStorage.removeItem('access_token')
      return
    }

    if (token) {
      try {
        currentUser.value = await authApi.me()
        isAuthenticated.value = true
      } catch {
        // Token invalid - clear both tokens
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        currentUser.value = null
        isAuthenticated.value = false
      }
    }
  }

  // Setup auth event listeners (call this once in App.vue)
  const setupAuthListeners = () => {
    window.addEventListener('auth:logout', () => {
      logout()
    })
  }

  return {
    // State
    currentUser,
    isAuthenticated,
    isGoogleLoaded,

    // Methods
    handleLoginSuccess,
    handleRegisterSuccess,
    logout,
    initializeGoogle,
    loadGoogleScript,
    checkSession,
    setupAuthListeners,
  }
}

// Add Google types
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: GoogleInitConfig) => void
          renderButton: (element: HTMLElement, config: GoogleButtonConfig) => void
          prompt: () => void
          disableAutoSelect: () => void
        }
      }
    }
  }
}
