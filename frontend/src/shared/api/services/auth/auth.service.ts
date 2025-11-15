import { API_URL } from '@/shared/config/api-url';
import { axiosClassic } from '../../api';
import type {
  RegisterDto,
  LoginDto,
  LoginResponse,
  RegisterResponse,
} from '@/shared/types/auth.type';
import { removeTokenFromStorage, saveTokenStorage } from './token.service';

class AuthService {
  async login(dto: LoginDto) {
    const response = await axiosClassic<LoginResponse>({
      url: API_URL.auth.login(),
      method: 'POST',
      data: { ...dto, grant_type: 'password' },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    if (response.data.access_token) {
      saveTokenStorage(response.data.access_token, response.data.refresh_token);
    }

    return response;
  }

  async register(dto: RegisterDto) {
    return await axiosClassic.post<RegisterResponse>(
      API_URL.auth.register(),
      dto
    );
  }

  async logout() {
    const response = await axiosClassic({
      url: API_URL.auth.logout(),
      method: 'POST',
    });

    if (response.data) removeTokenFromStorage();

    return response;
  }
}

export const authService = new AuthService();
