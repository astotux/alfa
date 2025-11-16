from services.llm_service import get_llm_response

class MemoryService:
    def __init__(self):
        self.memory = {}  # user_id -> list of messages

    def add_message(self, user_id: int, message: str):
        if user_id not in self.memory:
            self.memory[user_id] = []
        self.memory[user_id].append(message)
        # Автоматическая суммаризация при превышении длины
        if len("\n".join(self.memory[user_id])) > 3000:
            self._summarize_memory(user_id)

    def get_summary(self, user_id: int) -> str:
        return "\n".join(self.memory.get(user_id, []))

    def clear(self, user_id: int):
        """Очищает историю конкретного пользователя"""
        if user_id in self.memory:
            del self.memory[user_id]

    def sync_from_messages(self, user_id: int, messages: list):
        """Синхронизирует память с сообщениями из диалога"""
        self.memory[user_id] = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                self.memory[user_id].append(f"Пользователь: {content}")
            elif role == "assistant":
                self.memory[user_id].append(f"Ассистент: {content}")

    async def _summarize_memory(self, user_id: int):
        full_context = "\n".join(self.memory[user_id])
        summary_prompt = f"Сделай краткую выжимку из истории диалога, сохранив ключевые моменты: {full_context}"
        summary = await get_llm_response(summary_prompt, "", "Ты помощник по сжатию контекста диалога. Верни краткое резюме.")
        self.memory[user_id] = [f"Краткое содержание предыдущего диалога: {summary}"]

# Глобальный экземпляр — один на всё приложение
memory = MemoryService()