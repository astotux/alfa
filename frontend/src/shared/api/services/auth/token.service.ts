import Cookies from 'js-cookie';

export const COOKIES_ENUM = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
} as const;

export const removeTokenFromStorage = () => {
  Cookies.remove(COOKIES_ENUM.ACCESS_TOKEN);
};

export const saveTokenStorage = (accessToken: string) => {
  Cookies.set(COOKIES_ENUM.ACCESS_TOKEN, accessToken, {
    domain: 'localhost', // Заменить на переменную в .env
    sameSite: 'Strict',
    expires: 1,
  });
};

export const getAccessToken = () => {
  return Cookies.get(COOKIES_ENUM.ACCESS_TOKEN) || null;
};
