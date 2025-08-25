# Context-Aware Agent Routing System

## Overview

The improved routing system now uses a **Router Agent** that analyzes both the current user query AND the conversation context to make intelligent routing decisions. This ensures that follow-up questions are routed to the appropriate specialist agent.

## How It Works

### Step 1: Context Analysis
The Router Agent receives the conversation history in this format:
```
[Agent Name]: Previous response text
```

This allows the Router Agent to understand:
- Which agent was previously active
- What topic was being discussed
- Whether the current query is a follow-up

### Step 2: Routing Decision
The Router Agent follows these priority rules:

1. **Context-Aware Follow-ups** (Highest Priority)
   - If a specialist agent recently responded AND the current query is a follow-up → Route to the same specialist
   - Follow-up indicators: "what about", "tell me more", "also", "and", "additionally", "furthermore"
   - Contextual pronouns: "it", "that", "those", "them", "this", "these"
   - Domain-related follow-ups: asking about "electives" after course discussion

2. **Explicit Domain Queries**
   - Course/Academic → Course Advisor
   - Poetry/Creative → University Poet
   - Schedule/Calendar → Scheduling Assistant
   - General/Unclear → Triage Agent

### Step 3: Direct Agent Execution
Once the Router Agent decides, the system directly calls the appropriate specialist agent.

## Example Scenarios

### Scenario 1: Course Discussion with Follow-up
```
User: "What courses should I take next semester if I'm interested in data science?"
→ Router Agent decides: "Course Advisor"
→ Course Advisor responds with course recommendations

User: "What about electives?"
→ Router Agent sees context: [Course Advisor] discussed courses
→ Router Agent decides: "Course Advisor" (context-aware follow-up)
→ Course Advisor responds about electives
```

### Scenario 2: Poetry Request with Follow-up
```
User: "Write me a poem about the university cafeteria."
→ Router Agent decides: "University Poet"
→ University Poet responds with haiku

User: "Write another one about the library"
→ Router Agent sees context: [University Poet] wrote poetry
→ Router Agent decides: "University Poet" (context-aware follow-up)
→ University Poet responds with another haiku
```

### Scenario 3: Topic Change (Context Override)
```
User: "What courses should I take for computer science?"
→ Router Agent decides: "Course Advisor"
→ Course Advisor responds with CS course recommendations

User: "Write me a haiku about studying"
→ Router Agent sees context: [Course Advisor] discussed courses
→ Router Agent decides: "University Poet" (explicit poetry request overrides context)
→ University Poet responds with haiku
```

## Technical Implementation

### Router Agent Instructions
The Router Agent has detailed instructions that include:
- Available agent specializations
- Context analysis rules
- Follow-up detection patterns
- Specific examples with conversation context

### Conversation Context Format
```python
# Previous messages are formatted as:
agent_context = f"[{msg['sender']}]: {msg['text']}"
conversation_history.append({"role": "assistant", "content": agent_context})
```

### Agent Mapping
```python
agent_mapping = {
    "Course Advisor": course_advisor_agent,
    "University Poet": university_poet_agent,
    "Scheduling Assistant": scheduling_agent,
    "Triage Agent": triage_agent
}
```

## Benefits

✅ **Context Awareness**: Follow-up questions stay with the appropriate specialist
✅ **Intelligent Routing**: AI-powered decisions instead of simple keyword matching
✅ **Correct Display Names**: Frontend shows the actual responding agent
✅ **Conversation Continuity**: Natural conversation flow with specialists
✅ **Fallback Safety**: Keyword-based routing if Router Agent fails

## Debug Output

The system provides detailed debug output to track routing decisions:
```
DEBUG - Conversation context for Router Agent:
  1. user: What courses should I take for computer science?
  2. assistant: [Course Advisor]: I recommend CS320 and STAT210...
  3. user: What about electives?

DEBUG - Router Agent decision: 'Course Advisor'
DEBUG - Selected agent: Course Advisor
DEBUG - Final responding agent: Course Advisor
```

This ensures that the frontend correctly displays "Course Advisor" for both the initial question and the follow-up about electives.
