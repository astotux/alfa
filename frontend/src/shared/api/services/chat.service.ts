import { API_URL } from '@/shared/config/api-url';
import { axiosWithAuth } from '../api';
import type {
  CreateChatDto,
  CreateChatResponse,
  CreateMessageDto,
  GetChatResponse,
  GetChatsResponse,
} from '@/shared/types/chat.type';

class ChatService {
  async getChats() {
    return await axiosWithAuth.get<GetChatsResponse>(API_URL.chat.getChats());
  }

  async getChat({ id }: { id: string }) {
    return await axiosWithAuth.get<GetChatResponse>(
      API_URL.chat.getCurrentChat(id)
    );
  }

  async createChat(dto: CreateChatDto) {
    return await axiosWithAuth.post<CreateChatResponse>(
      API_URL.chat.createChat(),
      dto
    );
  }

  async deleteChat({ id }: { id: string }) {
    return await axiosWithAuth.delete(API_URL.chat.deleteChat(id));
  }

  async createMessage(dto: CreateMessageDto) {
    return await axiosWithAuth.post(API_URL.chat.createMessage(), dto);
  }
}

export const chatService = new ChatService();
