# Ask UNE - University Multi-Agent Support System

A sophisticated AI-powered university support system that uses multiple specialized agents to provide intelligent assistance to students. Built with React frontend and Django backend, featuring OpenAI's multi-agent architecture with context-aware routing and `gpt-4o-mini` model.

## 🎯 Overview

Ask UNE is an intelligent university support chatbot that uses a **Router Agent** to analyze queries and conversation context, then routes to specialized AI agents with visual distinction and conversation memory:

- **📚 Course Advisor**: Helps with course selection, academic planning, and study recommendations
- **🎭 University Poet**: Creates haiku about campus life and culture
- **📅 Scheduling Assistant**: Provides class times, exam schedules, and academic dates
- **🎯 Triage Agent**: Handles general conversations and unclear requests
- **🔀 Router Agent**: Analyzes queries and conversation context to determine optimal routing

## ✨ Key Features

- **🤖 Context-Aware Routing**: Router Agent analyzes conversation history to maintain context for follow-up questions
- **🎨 Visual Agent Distinction**: Each agent has unique icons and colors in the frontend
- **🧠 Conversation Memory**: Follow-up questions automatically route to the same specialist agent
- **📝 Rich Text Formatting**: Supports bold text, proper line breaks, and structured responses
- **💾 Session Management**: Persistent chat sessions with conversation history
- **🔧 Tool Integration**: Agents can call external functions for course lookup and calendar data
- **⚡ Real-time Chat**: Responsive chat interface with loading states and typing indicators
- **🔄 Extensible Design**: Easy to add new agents with automatic routing integration

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
| Course Advisor | 📚 | Green | Course selection, academic planning, degree requirements, study recommendations |
| University Poet | 🎭 | Purple | Haiku and poetry about campus life and culture |
| Scheduling Assistant | 📅 | Orange | Class schedules, exam dates, academic calendar |
| Triage Agent | 🎯 | Teal | General conversations and unclear requests |
| Router Agent | 🔀 | - | Internal routing logic (not visible to users) |
| You (User) | 👤 | Blue | User messages |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key with access to `gpt-4o-mini` model
- OpenAI Agents SDK (`pip install openai-agents` or similar)

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
- **AI-Powered Routing**: Router Agent analyzes queries to determine the best specialist, then directly executes the appropriate agent
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

- **Router Agent**: `gpt-4o-mini` for analyzing queries and conversation context to determine routing
- **Course Advisor**: `gpt-4o-mini` with course lookup tools for academic planning
- **University Poet**: `gpt-4o-mini` optimized for creative haiku generation about campus life
- **Scheduling Assistant**: `gpt-4o-mini` with academic calendar tools for dates and schedules
- **Triage Agent**: `gpt-4o-mini` for handling general conversations and unclear requests

## 🧠 How the Router Agent System Works

The system uses a sophisticated two-step process for intelligent query routing:

### Step 1: Context-Aware Analysis
The **Router Agent** analyzes both the current query and conversation history:
- **Conversation Context**: Previous agent responses are formatted as `[Agent Name]: response text`
- **Follow-up Detection**: Identifies contextual indicators like "what about", "tell me more", pronouns
- **Domain Analysis**: Recognizes course-related, poetry, scheduling, or general queries

### Step 2: Direct Agent Execution
Once routing is determined, the system directly executes the appropriate specialist agent:
- **Clean History**: Selected agent receives conversation history without agent name prefixes
- **Natural Responses**: Agents respond naturally without `[Agent Name]:` prefixes
- **Correct Attribution**: Frontend displays the actual responding agent with proper icons/colors

### Example Flow
```
User: "What courses should I take for data science?"
→ Router Agent analyzes: course-related query
→ Router Agent decides: "Course Advisor"
→ System executes: Course Advisor with clean conversation history
→ Course Advisor responds: course recommendations
→ Frontend displays: 📚 Course Advisor

User: "What about electives?" (follow-up)
→ Router Agent sees: [Course Advisor]: previous course discussion
→ Router Agent decides: "Course Advisor" (context-aware follow-up)
→ System executes: Course Advisor
→ Course Advisor responds: elective recommendations
→ Frontend displays: 📚 Course Advisor
```

### Context-Aware Features
- **Follow-up Questions**: Automatically route to the same specialist agent
- **Topic Changes**: Override context when user explicitly changes topics
- **Conversation Memory**: Maintain context across multiple exchanges
- **Fallback Safety**: Keyword-based routing if Router Agent fails

### Adding New Agents

The system uses the Router Agent for intelligent routing. To add a new agent:

1. **Create the agent in `agents_integration.py`**:
   ```python
   new_agent = Agent(
       name="New Agent",
       instructions="Your agent instructions here",
       tools=[your_tools],  # Optional: add function tools
       model="gpt-4o-mini",  # Use the configured model
   )
   ```

2. **Update the Router Agent instructions** to include your new agent:
   ```python
   # In the router_agent instructions, add your agent to the routing rules:
   "- ANY question about [your domain] → New Agent\n"

   # Add to the critical instruction list:
   "New Agent\n"

   # Add routing examples:
   "User: 'Example query for new agent' → New Agent\n"
   ```

3. **Add agent to the mapping in `run_triage_and_handle()` function**:
   ```python
   # Update the agent_mapping dictionary
   agent_mapping = {
       "Course Advisor": course_advisor_agent,
       "University Poet": university_poet_agent,
       "Scheduling Assistant": scheduling_agent,
       "Triage Agent": triage_agent,
       "New Agent": new_agent  # Add this line
   }
   ```

4. **Update the parsing logic** (if needed):
   ```python
   # Add to the fallback content analysis in run_triage_and_handle()
   elif any(word in routing_decision.lower() for word in ['new', 'agent', 'keywords']):
       routing_decision = "New Agent"
   ```

5. **Update frontend agent list in `App.jsx`** (optional for visual indicators):
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

- **Router Agent System**: Two-step process with context-aware routing and direct agent execution
- **Context-Aware Routing**: Analyzes conversation history to maintain context for follow-up questions
- **Session Management**: UUID-based sessions with persistent message history
- **Visual Agent Distinction**: Each agent has unique icons and colors for easy identification
- **Conversation Memory**: Follow-up questions automatically route to the same specialist agent
- **Clean Response Format**: Agent responses without name prefixes for natural conversation flow
- **Rich Text Formatting**: Support for bold text, line breaks, and structured responses
- **Tool Integration**: Function tools for course lookup, calendar data, and external integrations
- **Fallback Safety**: Keyword-based routing if Router Agent fails
- **Debug Logging**: Comprehensive logging for troubleshooting routing decisions and agent behavior

## 🧪 Testing

### Example Conversation Flows

#### Context-Aware Course Discussion:
1. **Initial Query**: "What courses should I take next semester if I'm interested in data science?"
   - *Router Agent*: Analyzes query → Routes to Course Advisor
   - *Response from*: 📚 **Course Advisor** (course recommendations)
2. **Follow-up**: "What about electives?"
   - *Router Agent*: Sees `[Course Advisor]: previous response` → Routes to Course Advisor
   - *Response from*: 📚 **Course Advisor** (elective recommendations)
3. **Follow-up**: "Tell me more about those prerequisites"
   - *Router Agent*: Context-aware follow-up → Routes to Course Advisor
   - *Response from*: 📚 **Course Advisor** (prerequisite details)

#### Topic Change Example:
1. **Course Query**: "What courses should I take for computer science?"
   - *Response from*: 📚 **Course Advisor**
2. **Topic Change**: "Write me a poem about the university cafeteria"
   - *Router Agent*: Explicit poetry request overrides context → Routes to University Poet
   - *Response from*: 🎭 **University Poet** (haiku about cafeteria)
3. **Poetry Follow-up**: "Write another one about the library"
   - *Router Agent*: Poetry context + follow-up → Routes to University Poet
   - *Response from*: 🎭 **University Poet** (haiku about library)

#### Scheduling Flow:
1. **Schedule Query**: "When do final exams start this semester?"
   - *Response from*: 📅 **Scheduling Assistant**
2. **Follow-up**: "What about registration deadlines?"
   - *Response from*: 📅 **Scheduling Assistant** (maintains context)

### Quick Test Queries

- **Course Advisor**: "What courses should I take for computer science?"
- **University Poet**: "Write me a haiku about campus life"
- **Scheduling Assistant**: "When is the semester deadline?"
- **Context Test**: Ask "What about electives?" after any course discussion
- **Topic Change Test**: Switch from courses to poetry to test context override

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

### Router Agent System (Latest)
- **Context-Aware Routing**: Router Agent analyzes conversation history to maintain context for follow-up questions
- **Two-Step Process**: Router Agent determines routing, then system directly executes the appropriate specialist
- **Clean Response Format**: Eliminated agent name prefixes from responses for natural conversation flow
- **Improved Agent Attribution**: Frontend correctly displays which specialist agent responded
- **Enhanced Course Detection**: Explicit routing rules ensure course questions go to Course Advisor
- **Fallback Safety**: Robust parsing with keyword-based fallback if Router Agent fails

### Previous Improvements
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
- **Router Agent Architecture**: Two-step routing process with context analysis and direct execution
- **Enhanced Parsing Logic**: Robust handling of Router Agent responses with fallback content analysis
- **Model Optimization**: All agents use `gpt-4o-mini` for cost-effective performance
- **Response Cleaning**: Separate conversation histories for routing vs. execution to eliminate prefixes
- **Error Handling**: Comprehensive error handling with keyword-based routing fallback
- **Frontend Enhancements**: Correct agent attribution and visual distinction

## 🐛 Troubleshooting

### Common Issues

1. **"Wrong agent selected" or "Only Triage Agent showing"**
   - Check Router Agent debug logs: `DEBUG - Router Agent decision`
   - Verify OpenAI API key is set correctly
   - Look for parsing issues in `DEBUG - Router Agent cleaned decision`
   - Ensure Router Agent instructions are not being overridden

2. **"Agent responses have [Agent Name]: prefix"**
   - This indicates the clean conversation history isn't being used
   - Check that `agent_input_messages` (not `router_input_messages`) is used for agent execution
   - Verify the conversation history separation logic

3. **"Follow-up questions not maintaining context"**
   - Check that conversation history includes previous agent responses
   - Verify Router Agent sees `[Agent Name]: previous response` format in debug logs
   - Ensure follow-up indicators are being detected

4. **"Router Agent giving advice instead of agent names"**
   - Check Router Agent instructions emphasize "ONLY the agent name"
   - Verify parsing logic handles long responses and extracts agent names
   - Look for content analysis fallback in debug logs

5. **"Backend connection errors"**
   - Ensure Django server is running on port 8000
   - Check that virtual environment is activated
   - Verify all dependencies including OpenAI Agents SDK are installed

6. **"Frontend not updating"**
   - Check that Vite dev server is running
   - Verify hot module replacement is working
   - Clear browser cache if needed

### Debug Output Examples

**Successful Routing:**
```
DEBUG - Router Agent decision: 'Course Advisor'
DEBUG - Selected agent: Course Advisor
DEBUG - Running Course Advisor with clean conversation history
DEBUG - Final responding agent: Course Advisor
```

**Context-Aware Follow-up:**
```
DEBUG - Conversation context for Router Agent:
  1. user: What courses should I take for data science?
  2. assistant: [Course Advisor]: I recommend CS320 and STAT210...
  3. user: What about electives?
DEBUG - Router Agent decision: 'Course Advisor'
DEBUG - Selected agent: Course Advisor
```

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
