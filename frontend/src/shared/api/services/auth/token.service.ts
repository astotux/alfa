import Cookies from 'js-cookie';

export const COOKIES_ENUM = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
} as const;

export const removeTokenFromStorage = () => {
  Cookies.remove(COOKIES_ENUM.ACCESS_TOKEN);
};

export const saveTokenStorage = (accessToken: string, refreshToken: string) => {
  Cookies.set(COOKIES_ENUM.ACCESS_TOKEN, accessToken, {
    domain: 'localhost', // Заменить на переменную в .env
    sameSite: 'Strict',
    expires: 1,
  });

  Cookies.set(COOKIES_ENUM.REFRESH_TOKEN, refreshToken, {
    domain: 'localhost', // Заменить на переменную в .env
    sameSite: 'Strict',
    expires: 1,
  });
};

export const getAccessToken = () => {
  return Cookies.get(COOKIES_ENUM.ACCESS_TOKEN) || null;
};

export const getRefreshToken = () => {
  return Cookies.get(COOKIES_ENUM.REFRESH_TOKEN) || null;
};
