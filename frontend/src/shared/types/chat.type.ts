import type { Message } from "./message.type";

export type CreateChatDto = {
  question: string;
  chat_type?: string;
};

export type CreateChatResponse = {
  chatId: string;
  title: string;
  messages: Message[];
};

export type GetChatResponse = {
  chatId: string;
  title: string;
  messages: Message[];
};


export type CreateMessageDto = {
  role: string;
  content: string;
  chatId: string;
}

export type ChatListItem = {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  chatType?: string;
};

export type GetChatsResponse = ChatListItem[];