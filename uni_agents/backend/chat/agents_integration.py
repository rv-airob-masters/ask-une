import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from django.conf import settings

load_dotenv()
try:
    # Preferred: official Agents SDK
    from agents import Agent, Runner, tool, Handoff, function_tool
    from openai import OpenAI
except Exception:
    # fallback imports to make errors clear if the package differs
    raise ImportError("Could not import Agents SDK modules. Please ensure you installed the OpenAI Agents SDK per official docs.")

from .tools import course_lookup, academic_calendar

# OpenAI client (Responses API) - not used directly here, but SDK will use it under the hood
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable must be set.")

# Example function-tool wrappers so agents can call our local functions
@function_tool
def tool_course_lookup(topic: str = "data science", level: str = "undergrad", limit: int = 4) -> Dict:
    return course_lookup(topic=topic, level=level, limit=limit)

@function_tool
def tool_academic_calendar(query: str = "") -> Dict:
    return academic_calendar(query=query)

# Build specialist agents
course_advisor_agent = Agent(
    name="Course Advisor",
    instructions=(
        "You are Course Advisor. You answer course selection and academic planning questions in a helpful "
        "and factual tone. When helpful, call the 'tool_course_lookup' tool to fetch recommended courses. "
        "Ask follow-up questions only if necessary to recommend better courses (e.g., year, major, preferences)."
    ),
    tools=[tool_course_lookup],
    model="gpt-4o-mini",
)

university_poet_agent = Agent(
    name="University Poet",
    instructions=(
        "You are University Poet. You respond ONLY in haiku (5-7-5 syllables) about campus culture and social life. "
        "If the user asks for schedules or course advice, politely refuse and suggest the appropriate assistant by name."
    ),
    tools=[],
    model="gpt-4o-mini",
)

scheduling_agent = Agent(
    name="Scheduling Assistant",
    instructions=(
        "You are Scheduling Assistant. Provide class times, exam schedules, and key academic dates in concise, factual sentences. "
        "Use the 'tool_academic_calendar' to fetch calendar facts if needed."
    ),
    tools=[tool_academic_calendar],
    model="gpt-4o-mini",
)

# Triage agent with handoffs to available specialists
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are the Triage Agent. Decide which specialist should handle the user's request: Course Advisor (courses/planning), "
        "University Poet (poems/haiku about campus/social life), or Scheduling Assistant (dates/schedules). "
        "If uncertain, ask a one-sentence clarifying question. If you decide a specific specialist should handle the request, use a handoff."
    ),
    # register handoff options (agents-as-tools)
    handoffs=[course_advisor_agent, university_poet_agent, scheduling_agent],
    model="gpt-4o-mini",
)

# Runner to execute agent runs on demand
runner = Runner()

def determine_agent_from_content(user_text: str, response_text: str) -> str:
    """
    Fallback method to determine which agent should have responded based on content analysis.
    """
    user_lower = user_text.lower()
    response_lower = response_text.lower()

    # Check for haiku patterns (University Poet)
    lines = response_text.strip().split('\n')
    if len(lines) == 3 or 'haiku' in user_lower or 'poem' in user_lower:
        # Check if it looks like a haiku structure
        if len(lines) >= 3:
            return "University Poet"

    # Check for course-related keywords (Course Advisor)
    course_keywords = ['course', 'class', 'major', 'degree', 'study', 'academic', 'curriculum', 'credit']
    if any(keyword in user_lower for keyword in course_keywords):
        return "Course Advisor"

    # Check for schedule-related keywords (Scheduling Assistant)
    schedule_keywords = ['schedule', 'time', 'exam', 'calendar', 'date', 'when', 'semester', 'deadline']
    if any(keyword in user_lower for keyword in schedule_keywords):
        return "Scheduling Assistant"

    # Default to Triage Agent
    return "Triage Agent"

async def run_triage_and_handle(session_messages: List[Dict[str, Any]], user_text: str) -> Dict[str, Any]:
    """
    Run triage agent with session context; execute handoffs / tools as requested and return final response.
    session_messages: list of {'sender':..., 'text':...} (most recent first or in order).
    Returns: { 'agent': agent_name, 'text': ..., 'tool_calls': [...], 'events': [...] }
    """
    # Convert session messages to the format expected by the SDK
    conversation_history = []
    for msg in session_messages[:-1]:  # exclude the current user message
        if msg['sender'] == 'user':
            conversation_history.append({"role": "user", "content": msg['text']})
        elif msg['sender'] not in ['tool']:  # agent messages
            conversation_history.append({"role": "assistant", "content": msg['text']})

    # Add current user message
    input_messages = conversation_history + [{"role": "user", "content": user_text}]

    try:
        # Run triage agent with conversation history
        result = await runner.run(triage_agent, input_messages)

        # Debug: Print the result structure to understand what we're getting
        print(f"DEBUG - Result type: {type(result)}")
        print(f"DEBUG - Result attributes: {dir(result)}")
        if hasattr(result, '__dict__'):
            print(f"DEBUG - Result dict: {result.__dict__}")

        # Extract the final output
        final_output = result.final_output if hasattr(result, 'final_output') else str(result)

        # Determine which agent actually provided the response
        responding_agent_name = "Triage Agent"  # Default

        # Check various possible attributes for agent information
        if hasattr(result, 'messages') and result.messages:
            print(f"DEBUG - Messages found: {len(result.messages)}")
            # Look through the messages to find the last agent that spoke
            for i, message in enumerate(result.messages):
                print(f"DEBUG - Message {i}: {type(message)}, attributes: {dir(message)}")
                if hasattr(message, 'sender') and message.sender:
                    print(f"DEBUG - Message {i} sender: {message.sender}")
                    if message.sender != 'user':
                        responding_agent_name = message.sender

        # Check if result has agent info
        if hasattr(result, 'agent') and result.agent:
            print(f"DEBUG - Agent found: {result.agent}")
            if hasattr(result.agent, 'name'):
                responding_agent_name = result.agent.name
                print(f"DEBUG - Agent name: {responding_agent_name}")

        # Check for active_agent or current_agent
        if hasattr(result, 'active_agent'):
            print(f"DEBUG - Active agent: {result.active_agent}")
            if hasattr(result.active_agent, 'name'):
                responding_agent_name = result.active_agent.name

        # Extract tool calls if any
        tool_calls = []
        if hasattr(result, 'tool_calls') and result.tool_calls:
            tool_calls = result.tool_calls
        elif hasattr(result, 'messages'):
            for message in result.messages:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls.extend(message.tool_calls)

        # Fallback: Try to determine agent based on content and user query
        if responding_agent_name == "Triage Agent":
            responding_agent_name = determine_agent_from_content(user_text, final_output)

        print(f"DEBUG - Final responding agent: {responding_agent_name}")
        print(f"DEBUG - Final output: {final_output}")

        return {
            "agent": responding_agent_name,
            "text": final_output,
            "tool_calls": tool_calls,
            "events": getattr(result, 'events', [])
        }

    except Exception as e:
        # Fallback response
        return {
            "agent": "Triage Agent",
            "text": f"I'm here to help! You said: {user_text}. How can I assist you with courses, schedules, or campus life?",
            "tool_calls": [],
            "events": []
        }
