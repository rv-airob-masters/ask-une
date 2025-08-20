# Ask UNE - University Multi-Agent Support System

A sophisticated AI-powered university support system that uses multiple specialized agents to provide intelligent assistance to students. Built with React frontend and Django backend, featuring OpenAI's multi-agent architecture.

## 🎯 Overview

Ask UNE is an intelligent university support chatbot that routes student queries to specialized AI agents:

- **Course Advisor**: Helps with course selection and academic planning
- **University Poet**: Creates haiku about campus life and culture  
- **Scheduling Assistant**: Provides class times, exam schedules, and academic dates
- **Triage Agent**: Intelligently routes queries to the appropriate specialist

## 🏗️ Architecture

```
ask_une/
├── frontend/          # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx    # Main chat interface
│   │   └── main.jsx   # React entry point
│   └── package.json
└── uni_agents/
    └── backend/       # Django REST API
        ├── backend/   # Django project settings
        └── chat/      # Chat app with agent integration
            ├── models.py           # Session & Message models
            ├── views.py            # API endpoints
            ├── agents_integration.py # Multi-agent system
            └── tools.py            # Course lookup & calendar tools
```

## ✨ Features

- **Multi-Agent Intelligence**: Specialized agents for different types of queries
- **Session Management**: Persistent chat sessions with conversation history
- **Tool Integration**: Agents can call external functions for data lookup
- **Real-time Chat**: Responsive chat interface with loading states
- **Extensible Design**: Easy to add new agents and tools

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd ask_une/uni_agents/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   # Create .env file in backend directory
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start Django server**
   ```bash
   python manage.py runserver
   ```

   ✅ **Backend should be running at**: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ask_une/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Open browser**
   ```
   http://localhost:5173
   ```

   ✅ **Frontend should be running at**: `http://localhost:5173`

### ⚠️ **Important Notes**

- **CORS**: Backend is configured to allow all hosts for development
- **API Endpoints**: Frontend uses `/api/message/` for chat functionality
- **Session Management**: Sessions are automatically created and persisted in localStorage
- **Environment**: Make sure to set `OPENAI_API_KEY` before testing agent functionality

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
```

### Adding New Agents

1. **Create agent in `agents_integration.py`**:
   ```python
   new_agent = Agent(
       name="New Agent",
       instructions="Your agent instructions here",
       tools=[your_tools],
   )
   ```

2. **Add to triage handoffs**:
   ```python
   triage_agent = Agent(
       # ... existing config
       handoffs=[course_advisor_agent, university_poet_agent, scheduling_agent, new_agent],
   )
   ```

3. **Update runner**:
   ```python
   runner = Runner.from_agents([triage_agent, course_advisor_agent, university_poet_agent, scheduling_agent, new_agent], openai_api_key=OPENAI_API_KEY)
   ```

## 📡 API Endpoints

Base URL: `http://localhost:8000/api/`

- `GET /` - API information and available endpoints
- `POST /api/session/` - Create new chat session
- `POST /api/message/` - Send message to agents
- `POST /api/clear/` - Clear chat session
- `GET /api/history/<session_id>/` - Get session history
- `POST /api/chat/` - Alternative chat endpoint (compatibility)

## 🛠️ Development

### Project Structure

- **Frontend**: React 18 with Vite for fast development
- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: SQLite for development (easily configurable for production)
- **AI**: OpenAI Agents SDK for multi-agent orchestration

### Key Components

- **Session Management**: UUID-based sessions with message history
- **Agent Routing**: Intelligent triage system for query classification
- **Tool Calling**: Function tools for data lookup and external integrations
- **Error Handling**: Comprehensive error handling and logging

## 🧪 Testing

### Example Queries

Try these sample queries to test different agents:

- **Course Advisor**: "What courses should I take for data science?"
- **University Poet**: "Write me a haiku about the library"
- **Scheduling Assistant**: "When do final exams start?"

## 📦 Dependencies

### Backend
- Django 4.2+
- djangorestframework
- python-dotenv
- openai 1.0.0+
- openai-agents 0.1.0

### Frontend
- React 18.2.0
- react-dom 18.2.0
- Vite 4.0.0
- @vitejs/plugin-react 3.0.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

---

**Built with ❤️ for university students**
