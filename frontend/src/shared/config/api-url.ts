export const API_URL = {
  root: (url = '') => `${url ? url : ''}`,
  user: {
    getProfile: () => API_URL.root('/user/profile'),
  },
  chat: {
    getChats: () => API_URL.root('/chat/'),
    getCurrentChat: (id: string) => API_URL.root(`/chat/${id}`),
  },
  auth: {
    login: () => API_URL.root('/auth/login'),
    register: () => API_URL.root('/auth/register'),
    refreshTokens: () => API_URL.root('/auth/refresh'),
  },
};
