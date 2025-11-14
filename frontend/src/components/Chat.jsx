import { useState, useRef, useEffect } from "react";
import "./../assets/css/chat.css";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const esRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startStream = (prompt) => {
    if (esRef.current) {
      esRef.current.close();
    }

    setMessages((prev) => [...prev, { type: "user", text: prompt }]);

    setMessages((prev) => [...prev, { type: "bot", text: "" }]);

    const url = `http://127.0.0.1:8000/api/stream?prompt=${encodeURIComponent(prompt)}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = (e) => {
        try {
          const obj = JSON.parse(e.data);
      
          const text = obj?.choices?.[0]?.delta?.content;
      
          if (text) {
            setMessages((prev) => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage && lastMessage.type === "bot") {
                newMessages[newMessages.length - 1] = {
                  ...lastMessage,
                  text: lastMessage.text + text,
                };
              }
              return newMessages;
            });
          }
        } catch (err) {
          console.log("raw data:", e.data);
        }
      };

    es.addEventListener("done", (e) => {
      console.log("stream done");
      es.close();
    });

    es.onerror = (err) => {
      console.error("EventSource error", err);
      es.close();
    };
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      startStream(input);
      setInput("");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">Начните диалог, отправив сообщение</div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-message ${msg.type === "user" ? "user-message" : "bot-message"}`}
            >
              <div className="message-content">{msg.text || "..."}</div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Введите сообщение..."
          className="chat-input"
        />
        <button type="submit" className="chat-button">Отправить</button>
      </form>
    </div>
  );
}
