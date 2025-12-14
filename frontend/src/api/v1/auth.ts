import { api } from '@/api/client'
import type {
  AuthResponse,
  User,
  LoginRequest,
  RegisterRequest,
  GoogleAuthRequest,
  SetPasswordRequest,
  ChangePasswordRequest
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

  setPassword: (data: SetPasswordRequest) =>
    api.post<User>('/auth/set-password', data),

  changePassword: (data: ChangePasswordRequest) =>
    api.post<User>('/auth/change-password', data),

  verifyEmail: (token: string) =>
    api.post<User>(`/auth/verify-email?token=${encodeURIComponent(token)}`),

  resendVerification: () =>
    api.post<{ message: string }>('/auth/resend-verification'),
}
