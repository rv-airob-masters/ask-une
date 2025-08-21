# Ask UNE - University Multi-Agent Support System

A sophisticated AI-powered university support system that uses multiple specialized agents to provide intelligent assistance to students. Built with React frontend and Django backend, featuring OpenAI's multi-agent architecture with `gpt-4o-mini` model.

## 🎯 Overview

Ask UNE is an intelligent university support chatbot that routes student queries to specialized AI agents with visual distinction and conversation context awareness:

- **📚 Course Advisor**: Helps with course selection and academic planning
- **🎭 University Poet**: Creates haiku about campus life and culture
- **📅 Scheduling Assistant**: Provides class times, exam schedules, and academic dates
- **🎯 Triage Agent**: Intelligently routes queries to the appropriate specialist

## ✨ Key Features

- **🤖 Multi-Agent Intelligence**: Specialized agents for different types of queries
- **🎨 Visual Agent Distinction**: Each agent has unique icons and colors
- **🧠 Context Awareness**: Maintains conversation context for follow-up questions
- **📝 Rich Text Formatting**: Supports bold text, proper line breaks, and structured responses
- **💾 Session Management**: Persistent chat sessions with conversation history
- **🔧 Tool Integration**: Agents can call external functions for data lookup
- **⚡ Real-time Chat**: Responsive chat interface with loading states
- **🔄 Extensible Design**: Easy to add new agents and tools

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

## 🎨 Agent Visual Indicators

Each agent is visually distinguished with unique icons and colors:

| Agent | Icon | Color | Specialization |
|-------|------|-------|----------------|
| Course Advisor | 📚 | Green | Course selection, academic planning, degree requirements |
| University Poet | 🎭 | Purple | Haiku and poetry about campus life and culture |
| Scheduling Assistant | 📅 | Orange | Class schedules, exam dates, academic calendar |
| Triage Agent | 🎯 | Teal | Query routing and general assistance |
| You (User) | 👤 | Blue | User messages |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key with access to `gpt-4o-mini` model

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
   npm run dev
   ```

4. **Open browser**
   ```
   http://localhost:5174
   ```

   ✅ **Frontend should be running at**: `http://localhost:5174` (or next available port)

### ⚠️ **Important Notes**

- **Model Configuration**: All agents use `gpt-4o-mini` for cost-effective and fast responses
- **Agent Detection**: System automatically detects which agent should respond based on query content and conversation context
- **Context Awareness**: Follow-up questions maintain conversation context with the same specialist agent
- **Rich Formatting**: Responses support **bold text**, proper line breaks, and structured formatting
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

### Model Configuration

All agents are configured to use the `gpt-4o-mini` model for optimal performance and cost-effectiveness:

- **Course Advisor**: `gpt-4o-mini` with course lookup tools
- **University Poet**: `gpt-4o-mini` optimized for creative haiku generation
- **Scheduling Assistant**: `gpt-4o-mini` with academic calendar tools
- **Triage Agent**: `gpt-4o-mini` for intelligent query routing

### Adding New Agents

The system uses direct agent routing rather than SDK handoffs. To add a new agent:

1. **Create the agent in `agents_integration.py`**:
   ```python
   new_agent = Agent(
       name="New Agent",
       instructions="Your agent instructions here",
       tools=[your_tools],  # Optional: add function tools
       model="gpt-4o-mini",  # Use the configured model
   )
   ```

2. **Add routing logic in `determine_target_agent()` function**:
   ```python
   # Add detection keywords for your new agent
   new_agent_keywords = ['keyword1', 'keyword2', 'specific_phrase']
   if any(keyword in user_lower for keyword in new_agent_keywords):
       print(f"DEBUG - New agent query detected, routing to: New Agent")
       return "New Agent"
   ```

3. **Add agent selection in `run_triage_and_handle()` function**:
   ```python
   # Get the appropriate agent
   if target_agent_name == "Course Advisor":
       target_agent = course_advisor_agent
   elif target_agent_name == "University Poet":
       target_agent = university_poet_agent
   elif target_agent_name == "Scheduling Assistant":
       target_agent = scheduling_agent
   elif target_agent_name == "New Agent":  # Add this
       target_agent = new_agent
   else:
       target_agent = triage_agent
       target_agent_name = "Triage Agent"
   ```

4. **Update frontend agent list in `App.jsx`** (optional for visual indicators):
   ```javascript
   const agents = [
     // ... existing agents
     {
       name: "New Agent",
       icon: "🆕",
       color: "#your_color",
       description: "Your agent description"
     }
   ];
   ```

5. **Add CSS styling in `App.css`** (optional for visual distinction):
   ```css
   .message-sender[data-agent="New Agent"]::before {
     content: "🆕";
   }

   .message-sender[data-agent="New Agent"] {
     color: #your_color;
   }
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
- **Agent Routing**: Intelligent triage system for query classification with context awareness
- **Visual Distinction**: Each agent has unique icons and colors for easy identification
- **Context Preservation**: Follow-up questions maintain conversation context
- **Rich Text Formatting**: Support for bold text, line breaks, and structured responses
- **Tool Calling**: Function tools for data lookup and external integrations
- **Error Handling**: Comprehensive error handling and logging
- **Debug Logging**: Detailed logging for troubleshooting agent behavior

## 🧪 Testing

### Example Conversation Flows

#### Course Advisor Flow:
1. **Initial Query**: "What courses should I take for data science?"
   - *Response from*: 📚 **Course Advisor**
2. **Follow-up**: "Tell me more about CS320"
   - *Response from*: 📚 **Course Advisor** (maintains context)
3. **Follow-up**: "What are the prerequisites for that course?"
   - *Response from*: 📚 **Course Advisor** (continues context)

#### University Poet Flow:
1. **Poetry Request**: "Write me a haiku about the library"
   - *Response from*: 🎭 **University Poet**
2. **Follow-up**: "Write another one about studying"
   - *Response from*: 🎭 **University Poet** (maintains context)

#### Scheduling Assistant Flow:
1. **Schedule Query**: "When do final exams start?"
   - *Response from*: 📅 **Scheduling Assistant**
2. **Follow-up**: "What about midterm dates?"
   - *Response from*: 📅 **Scheduling Assistant** (maintains context)

### Quick Test Queries

- **Course Advisor**: "What courses should I take for computer science?"
- **University Poet**: "Write me a haiku about campus life"
- **Scheduling Assistant**: "When is the semester deadline?"
- **Context Test**: Ask a follow-up question after any specialist response

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

## 🔧 Recent Improvements

### Agent Detection & Context Awareness
- **Smart Agent Attribution**: System correctly identifies which specialist agent provided each response
- **Conversation Context**: Follow-up questions maintain context with the same agent
- **Fallback Logic**: Content-based agent detection when SDK handoffs aren't detected
- **Debug Logging**: Comprehensive logging for troubleshooting agent behavior

### Visual & UX Enhancements
- **Agent Icons**: Each agent has a unique emoji icon (📚📅🎭🎯👤)
- **Color Coding**: Distinct colors for each agent type
- **Rich Text Formatting**: Support for **bold text** and proper line breaks
- **Improved Readability**: Better spacing and formatting for structured responses

### Technical Improvements
- **Model Optimization**: All agents use `gpt-4o-mini` for cost-effective performance
- **Response Parsing**: Enhanced text cleaning and formatting
- **Error Handling**: Improved error handling and fallback responses
- **Frontend Enhancements**: Markdown support and better message rendering

## 🐛 Troubleshooting

### Common Issues

1. **"Only Triage Agent showing"**
   - Check that OpenAI API key is set correctly
   - Verify debug logs in Django terminal
   - Ensure follow-up questions use contextual language

2. **"Formatting issues in responses"**
   - Check that `white-space: pre-wrap` is applied in CSS
   - Verify markdown formatting is working in frontend
   - Look for escaped characters in debug logs

3. **"Backend connection errors"**
   - Ensure Django server is running on port 8000
   - Check that virtual environment is activated
   - Verify all dependencies are installed

4. **"Frontend not updating"**
   - Check that Vite dev server is running
   - Verify hot module replacement is working
   - Clear browser cache if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the details below.

### MIT License

```
MIT License

Copyright (c) 2024 Ask UNE - University Multi-Agent Support System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🆘 Support

For questions or issues:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

---

**Built with ❤️ for university students**
