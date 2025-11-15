import type { Message } from "./message.type";

export type CreateChatDto = {
  question: string;
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