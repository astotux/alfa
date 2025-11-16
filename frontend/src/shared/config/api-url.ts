export const API_URL = {
  root: (url = '') => `${url ? url : ''}`,
  user: {
    getProfile: () => API_URL.root('/user/profile'),
    getSyncToken: () => API_URL.root('/user/sync-token'),
  },
  chat: {
    getChats: (chatType?: string) => {
      const url = API_URL.root('/chats');
      return chatType ? `${url}?chat_type=${chatType}` : url;
    },
    getCurrentChat: (id: string) => API_URL.root(`/chat/${id}`),
    createChat: () => API_URL.root(`/chat`),
    deleteChat: (id: string) => API_URL.root(`/chat/${id}`),
    createMessage: () => API_URL.root(`/message`),
  },
  auth: {
    login: () => API_URL.root('/auth/login'),
    register: () => API_URL.root('/auth/register'),
    refreshTokens: () => API_URL.root('/auth/refresh'),
    logout: () => API_URL.root('/auth/logout'),
  },
};
