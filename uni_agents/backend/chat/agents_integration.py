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

        # Extract the final output
        final_output = result.final_output if hasattr(result, 'final_output') else str(result)

        # For now, return a simple response - handoffs would be handled automatically by the SDK
        return {
            "agent": "Triage Agent",
            "text": final_output,
            "tool_calls": [],
            "events": []
        }

    except Exception as e:
        # Fallback response
        return {
            "agent": "Triage Agent",
            "text": f"I'm here to help! You said: {user_text}. How can I assist you with courses, schedules, or campus life?",
            "tool_calls": [],
            "events": []
        }
