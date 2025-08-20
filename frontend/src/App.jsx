import { useState, useEffect } from "react";
import "./App.css";

const API_BASE = "/api"; // Using proxy, so no need for full URL

function App() {
  const [sessionId, setSessionId] = useState(localStorage.getItem("session_id"));
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sessionId) {
      createSession();
    } else {
      loadHistory();
    }
  }, [sessionId]);

  const createSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/session/`, { method: "POST" });
      const data = await res.json();
      setSessionId(data.session_id);
      localStorage.setItem("session_id", data.session_id);
      setError(null);
    } catch (err) {
      setError("Failed to create session. Please check if the backend is running.");
      console.error("Session creation error:", err);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history/${sessionId}/`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages.map(m => ({ sender: m.sender, text: m.text })));
      }
    } catch (err) {
      console.error("History loading error:", err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg = { sender: "You", text: input };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/message/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, text: input }),
      });
      
      const data = await res.json();
      setLoading(false);

      if (res.ok) {
        setMessages(prev => [...prev, { sender: data.agent, text: data.text }]);
        setInput("");
      } else {
        setMessages(prev => [...prev, { sender: "System", text: data.error || "Unknown error" }]);
        setError(data.error || "Failed to send message");
      }
    } catch (err) {
      setLoading(false);
      setError("Failed to send message. Please check if the backend is running.");
      setMessages(prev => [...prev, { sender: "System", text: "Connection error. Please try again." }]);
      console.error("Send message error:", err);
    }
  };

  const clearChat = async () => {
    try {
      const res = await fetch(`${API_BASE}/clear/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      localStorage.setItem("session_id", data.session_id);
      setMessages([]);
      setError(null);
    } catch (err) {
      setError("Failed to clear chat");
      console.error("Clear chat error:", err);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <h1>🎓 Ask UNE</h1>
          <p>University Multi-Agent Support System</p>
        </header>

        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        <div className="messages-container">
          {messages.length === 0 && !loading && (
            <div className="welcome-message">
              <h3>Welcome to Ask UNE! 👋</h3>
              <p>I'm here to help you with:</p>
              <ul>
                <li><strong>Course Advice:</strong> "What courses should I take for data science?"</li>
                <li><strong>Scheduling:</strong> "When do final exams start?"</li>
                <li><strong>Campus Poetry:</strong> "Write me a haiku about the library"</li>
              </ul>
              <p>Just type your question below to get started!</p>
            </div>
          )}
          
          {messages.map((message, idx) => (
            <div key={idx} className={`message ${message.sender === 'You' ? 'user' : 'agent'}`}>
              <div className="message-sender">{message.sender}</div>
              <div className="message-text">{message.text}</div>
            </div>
          ))}
          
          {loading && (
            <div className="message agent">
              <div className="message-sender">Agent</div>
              <div className="message-text loading">
                <span className="typing-indicator">Thinking</span>
                <span className="dots">...</span>
              </div>
            </div>
          )}
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about university life..."
              disabled={loading}
              className="message-input"
            />
            <button 
              onClick={sendMessage} 
              disabled={loading || !input.trim()}
              className="send-button"
            >
              Send
            </button>
            <button 
              onClick={clearChat} 
              disabled={loading}
              className="clear-button"
            >
              Clear
            </button>
          </div>
        </div>

        <footer className="chat-footer">
          <div className="session-info">
            Session: <code>{sessionId}</code>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
