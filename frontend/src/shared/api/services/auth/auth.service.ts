import { API_URL } from '@/shared/config/api-url';
import { axiosClassic } from '../../api';

class AuthService {
  async login(dto: any) {
    return await axiosClassic.post(API_URL.auth.login(), dto);
  }

  async register(dto: any) {
    return await axiosClassic.post(API_URL.auth.register(), dto);
  }

  async getNewTokens() {
    const response = await axiosClassic({
      url: API_URL.auth.refreshTokens(),
      method: 'POST',
    });

    return response;
  }
}

export const authService = new AuthService();
