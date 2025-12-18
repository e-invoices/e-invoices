import { api } from '@/api/client'
import type {
  AuthResponse,
  User,
  LoginRequest,
  RegisterRequest,
  GoogleAuthRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  SwitchOrganizationRequest,
  SwitchOrganizationResponse,
  UpdateProfileRequest,
  LinkGoogleRequest
} from '@/types/auth'

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<AuthResponse>('/auth/login', data),

  register: (data: RegisterRequest) =>
    api.post<AuthResponse>('/auth/register', data),

  googleAuth: (data: GoogleAuthRequest) =>
    api.post<AuthResponse>('/auth/google', data),

  me: () =>
    api.get<User>('/auth/me'),

  logout: () =>
    api.post<void>('/auth/logout'),

  // Request password reset email (for unauthenticated users - forgot password)
  forgotPassword: (data: ForgotPasswordRequest) =>
    api.post<{ message: string }>('/auth/forgot-password', data),

  // Request password reset email (for authenticated users - set/change password)
  requestPasswordReset: () =>
    api.post<{ message: string }>('/auth/request-password-reset'),

  // Reset password using token from email
  resetPassword: (data: ResetPasswordRequest) =>
    api.post<User>('/auth/reset-password', data),

  updateProfile: (data: UpdateProfileRequest) =>
    api.put<User>('/auth/profile', data),

  linkGoogle: (data: LinkGoogleRequest) =>
    api.post<User>('/auth/link-google', data),

  verifyEmail: (token: string) =>
    api.post<User>(`/auth/verify-email?token=${encodeURIComponent(token)}`),

  resendVerification: () =>
    api.post<{ message: string }>('/auth/resend-verification'),

  switchOrganization: (data: SwitchOrganizationRequest) =>
    api.post<SwitchOrganizationResponse>('/auth/switch-organization', data),
}
