import { useState, useEffect, useRef } from "react";
import "./App.css";

const API_BASE = "/api"; // Using proxy, so no need for full URL

function App() {
  const [sessionId, setSessionId] = useState(localStorage.getItem("session_id"));
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!sessionId) {
      createSession();
    } else {
      loadHistory();
    }
  }, [sessionId]);

  // Auto-focus input on component mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

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
        // Focus the input field after agent response
        setTimeout(() => {
          if (inputRef.current) {
            inputRef.current.focus();
          }
        }, 100);
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
      // Focus input after clearing chat
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);
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

  const formatMessage = (text) => {
    if (!text) return text;

    // Convert **bold** to <strong>
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Convert *italic* to <em>
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    return formatted;
  };

  const agents = [
    {
      name: "Course Advisor",
      icon: "📚",
      color: "#28a745",
      description: "Course selection and academic planning"
    },
    {
      name: "University Poet",
      icon: "🎭",
      color: "#6f42c1",
      description: "Haiku and poetry about campus life"
    },
    {
      name: "Scheduling Assistant",
      icon: "📅",
      color: "#fd7e14",
      description: "Class schedules and academic dates"
    },
    {
      name: "Triage Agent",
      icon: "🎯",
      color: "#17a2b8",
      description: "Query routing and general assistance"
    }
  ];

  const getActiveAgent = () => {
    if (messages.length === 0) return null;
    const lastMessage = messages[messages.length - 1];
    return lastMessage.sender !== 'You' ? lastMessage.sender : null;
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

        <div className="main-content">
          <aside className="sidebar">
            <h3>Available Agents</h3>
            <ul className="agent-list">
              {agents.map((agent) => (
                <li
                  key={agent.name}
                  className={`agent-item ${getActiveAgent() === agent.name ? 'active' : ''}`}
                  style={{ borderLeftColor: agent.color }}
                >
                  <span className="agent-icon">{agent.icon}</span>
                  <div>
                    <div style={{ color: agent.color, fontWeight: '600' }}>{agent.name}</div>
                    <div className="agent-description">{agent.description}</div>
                  </div>
                </li>
              ))}
            </ul>

            <div style={{ marginTop: '24px', padding: '16px', background: '#fff', borderRadius: '8px', border: '1px solid #e1e5e9' }}>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '0.9rem', color: '#333' }}>Session Info</h4>
              <div style={{ fontSize: '0.8rem', color: '#666', fontFamily: 'monospace' }}>
                {sessionId ? sessionId.substring(0, 8) + '...' : 'No session'}
              </div>
            </div>
          </aside>

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
              <div className="message-sender" data-agent={message.sender}>{message.sender}</div>
              <div
                className="message-text"
                dangerouslySetInnerHTML={{ __html: formatMessage(message.text) }}
              />
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
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <input
              ref={inputRef}
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
      </div>
    </div>
  );
}

export default App;
