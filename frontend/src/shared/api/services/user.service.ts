import { API_URL } from '@/shared/config/api-url';
import { axiosWithAuth } from '../api';

class UserService {
  async getProfile() {
    return await axiosWithAuth.get(API_URL.user.getProfile());
  }
}

export const userService = new UserService();
