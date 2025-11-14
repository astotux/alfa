import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/chat"; // ваш endpoint FastAPI

export const sendMessage = async (text) => {
  try {
    const response = await axios.post(API_URL, { message: text });
    return response.data; // ожидаем JSON { reply: "..."}
  } catch (error) {
    console.error(error);
    return { reply: "Ошибка сервера" };
  }
};
