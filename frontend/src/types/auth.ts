// User types
export interface User {
  id: number
  email: string
  name?: string
  full_name?: string
  auth_provider?: string
  picture_url?: string
  has_password?: boolean
  is_verified?: boolean
}

// Auth response from backend
export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
}

// Auth request types
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
}

export interface GoogleAuthRequest {
  credential: string
  is_registration?: boolean
}

// Password management
export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  token: string
  password: string
  confirm_password: string
}

export interface UpdateProfileRequest {
  full_name?: string
}

export interface LinkGoogleRequest {
  credential: string
}

// Google OAuth types
export interface GoogleCredentialResponse {
  credential: string
  select_by?: string
  clientId?: string
}

export interface GoogleButtonConfig {
  theme: 'outline' | 'filled_blue' | 'filled_black'
  size: 'large' | 'medium' | 'small'
  width?: number
  text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin'
  shape?: 'rectangular' | 'pill' | 'circle' | 'square'
  logo_alignment?: 'left' | 'center'
}

export interface GoogleInitConfig {
  client_id: string
  callback: (response: GoogleCredentialResponse) => void
  auto_select?: boolean
  cancel_on_tap_outside?: boolean
}

// Auth modal exposed methods
export interface LoginModalExposed {
  handleGoogleLogin: (response: GoogleCredentialResponse) => Promise<void>
  handleGoogleError: () => void
}

export interface RegisterModalExposed {
  handleGoogleRegister: (response: GoogleCredentialResponse) => Promise<void>
  handleGoogleError: () => void
}

// Organization switching
export interface SwitchOrganizationRequest {
  organization_id: number
}

export interface SwitchOrganizationResponse {
  access_token: string
  refresh_token: string
  token_type: string
  organization_id: number
  role: string
}
