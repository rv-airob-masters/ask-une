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
        "Use the 'tool_academic_calendar' tool to fetch calendar facts. When users ask about specific courses, "
        "include the course code in your query to get detailed schedule information. "
        "For general schedule questions, provide comprehensive semester information. "
        "Always format dates clearly and mention any important deadlines."
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

def format_agent_response(text: str) -> str:
    """
    Format agent responses for better readability.
    """
    if not isinstance(text, str):
        return str(text)

    # Add proper line breaks after numbered lists
    import re

    # Add line breaks before numbered items (1., 2., etc.)
    text = re.sub(r'(\d+\.\s\*\*)', r'\n\n\1', text)

    # Add line breaks after sentences that end with periods followed by numbers
    text = re.sub(r'(\.\s)(\d+\.\s)', r'\1\n\n\2', text)

    # Add line breaks before "Would you like" or similar closing questions
    text = re.sub(r'(\.\s)(Would you like|Do you need|Is there anything)', r'\1\n\n\2', text)

    # Clean up multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text

def determine_target_agent(user_text: str, session_messages: List[Dict[str, Any]] = None) -> str:
    """
    Determine which agent should handle the user's query based on content analysis and conversation context.
    This is the main routing logic that decides which specialist agent to use.
    """
    user_lower = user_text.lower()

    print(f"DEBUG - Routing analysis for: '{user_text}'")

    # First, check conversation context for follow-up questions
    if session_messages:
        # Look for the most recent non-user message to see which agent was active
        last_agent = None
        for msg in reversed(session_messages):
            if msg.get('sender') not in ['user', 'You', 'tool']:
                last_agent = msg.get('sender')
                break

        # If we have a recent specialist agent and this looks like a follow-up question
        if last_agent and last_agent != "Triage Agent":
            follow_up_indicators = [
                'tell me more', 'more details', 'what about', 'can you explain',
                'prerequisites', 'requirements', 'how about', 'what are the',
                'more information', 'details about', 'expand on', 'elaborate',
                'that course', 'those courses', 'about it', 'about that'
            ]

            # Check if this is a follow-up question
            if any(indicator in user_lower for indicator in follow_up_indicators):
                print(f"DEBUG - Follow-up detected, routing to: {last_agent}")
                return last_agent

            # Also check if the question is short and contextual (likely a follow-up)
            if len(user_text.split()) <= 8 and any(word in user_lower for word in ['it', 'that', 'this', 'them', 'those']):
                print(f"DEBUG - Contextual follow-up detected, routing to: {last_agent}")
                return last_agent

    # Check for poetry/haiku requests (University Poet)
    poetry_indicators = ['haiku', 'poem', 'poetry', 'verse', 'write me a', 'compose a']
    if any(indicator in user_lower for indicator in poetry_indicators):
        print(f"DEBUG - Poetry request detected, routing to: University Poet")
        return "University Poet"

    # Check for course-related queries (Course Advisor)
    course_keywords = [
        'course', 'courses', 'class', 'classes', 'major', 'degree', 'study', 'studying',
        'academic', 'curriculum', 'credit', 'credits', 'cs320', 'stat210', 'cs250', 'cs499',
        'computer science', 'data science', 'artificial intelligence', 'machine learning',
        'programming', 'statistics', 'undergraduate', 'graduate', 'what should i take',
        'recommend', 'recommendation', 'subject', 'subjects'
    ]
    if any(keyword in user_lower for keyword in course_keywords):
        print(f"DEBUG - Course query detected, routing to: Course Advisor")
        return "Course Advisor"

    # Check for schedule-related queries (Scheduling Assistant)
    schedule_keywords = [
        'schedule', 'time', 'exam', 'exams', 'calendar', 'date', 'dates', 'when',
        'semester', 'deadline', 'deadlines', 'final', 'finals', 'midterm', 'midterms',
        'start', 'end', 'begins', 'registration', 'when do', 'when does', 'when is'
    ]
    if any(keyword in user_lower for keyword in schedule_keywords):
        print(f"DEBUG - Schedule query detected, routing to: Scheduling Assistant")
        return "Scheduling Assistant"

    # Default to Triage Agent for general queries
    print(f"DEBUG - General query, routing to: Triage Agent")
    return "Triage Agent"

def determine_agent_from_content(user_text: str, response_text: str, session_messages: List[Dict[str, Any]] = None) -> str:
    """
    Fallback method to determine which agent should have responded based on content analysis and conversation context.
    """
    user_lower = user_text.lower()
    response_lower = response_text.lower()

    print(f"DEBUG - Analyzing user text: '{user_text}'")
    print(f"DEBUG - Response preview: '{response_text[:100]}...'")

    # First, check conversation context - if the last agent response was from a specialist,
    # and this seems like a follow-up, continue with the same agent
    if session_messages:
        # Look for the most recent non-user message to see which agent was active
        last_agent = None
        for msg in reversed(session_messages):
            if msg.get('sender') not in ['user', 'You', 'tool']:
                last_agent = msg.get('sender')
                print(f"DEBUG - Found last agent: {last_agent}")
                break

        # If we have a recent specialist agent and this looks like a follow-up question
        if last_agent and last_agent != "Triage Agent":
            follow_up_indicators = [
                'tell me more', 'more details', 'what about', 'can you explain',
                'prerequisites', 'requirements', 'how about', 'what are the',
                'more information', 'details about', 'expand on', 'elaborate',
                'that course', 'those courses', 'about it', 'about that'
            ]

            # Check if this is a follow-up question
            if any(indicator in user_lower for indicator in follow_up_indicators):
                print(f"DEBUG - Detected follow-up question, continuing with: {last_agent}")
                return last_agent

            # Also check if the question is short and contextual (likely a follow-up)
            if len(user_text.split()) <= 8 and any(word in user_lower for word in ['it', 'that', 'this', 'them', 'those']):
                print(f"DEBUG - Detected contextual follow-up, continuing with: {last_agent}")
                return last_agent

    # Check for poetry/haiku requests first (most specific)
    poetry_indicators = ['haiku', 'poem', 'poetry', 'verse', 'write me a', 'compose']
    if any(indicator in user_lower for indicator in poetry_indicators):
        print(f"DEBUG - Detected poetry request")
        return "University Poet"

    # Check response content for haiku patterns
    lines = response_text.strip().split('\n')
    if len(lines) == 3 and all(len(line.strip()) > 0 for line in lines):
        # Looks like a haiku structure
        print(f"DEBUG - Detected haiku structure in response")
        return "University Poet"

    # Check for course-related keywords (Course Advisor)
    course_keywords = [
        'course', 'courses', 'class', 'classes', 'major', 'degree', 'study', 'studying',
        'academic', 'curriculum', 'credit', 'credits', 'cs320', 'stat210', 'cs250', 'cs499',
        'computer science', 'data science', 'artificial intelligence', 'machine learning',
        'programming', 'statistics', 'undergraduate', 'graduate'
    ]
    if any(keyword in user_lower for keyword in course_keywords):
        print(f"DEBUG - Detected course-related keywords")
        return "Course Advisor"

    # Check for schedule-related keywords (Scheduling Assistant)
    schedule_keywords = [
        'schedule', 'time', 'exam', 'exams', 'calendar', 'date', 'dates', 'when',
        'semester', 'deadline', 'deadlines', 'final', 'finals', 'midterm', 'midterms',
        'start', 'end', 'begins', 'registration'
    ]
    if any(keyword in user_lower for keyword in schedule_keywords):
        print(f"DEBUG - Detected schedule-related keywords")
        return "Scheduling Assistant"

    # Check response content for agent-specific patterns
    if any(word in response_lower for word in ['cs320', 'stat210', 'cs250', 'cs499', 'recommended courses', 'course selection']):
        print(f"DEBUG - Detected course content in response")
        return "Course Advisor"

    if any(word in response_lower for word in ['haiku', 'syllables', 'poem', 'verse']):
        print(f"DEBUG - Detected poetry content in response")
        return "University Poet"

    if any(word in response_lower for word in ['schedule', 'exam', 'calendar', 'semester', 'deadline']):
        print(f"DEBUG - Detected schedule content in response")
        return "Scheduling Assistant"

    # Default to Triage Agent for general queries
    print(f"DEBUG - Defaulting to Triage Agent")
    return "Triage Agent"

async def run_triage_and_handle(session_messages: List[Dict[str, Any]], user_text: str) -> Dict[str, Any]:
    """
    Determine the appropriate agent and run it directly based on query analysis.
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

    # Determine which agent should handle this query
    target_agent_name = determine_target_agent(user_text, session_messages)
    print(f"DEBUG - Target agent determined: {target_agent_name}")

    # Get the appropriate agent
    if target_agent_name == "Course Advisor":
        target_agent = course_advisor_agent
    elif target_agent_name == "University Poet":
        target_agent = university_poet_agent
    elif target_agent_name == "Scheduling Assistant":
        target_agent = scheduling_agent
    else:
        target_agent = triage_agent
        target_agent_name = "Triage Agent"

    try:
        # Run the selected agent directly
        result = await runner.run(target_agent, input_messages)

        # Extract and clean the final output
        final_output = result.final_output if hasattr(result, 'final_output') else str(result)

        # Clean up the output
        if isinstance(final_output, str):
            # Remove extra quotes and unescape newlines
            if final_output.startswith('"') and final_output.endswith('"'):
                final_output = final_output[1:-1]

            # Unescape common escape sequences
            final_output = final_output.replace('\\n', '\n')
            final_output = final_output.replace('\\"', '"')
            final_output = final_output.replace('\\\\', '\\')
            final_output = final_output.replace('\\t', '\t')

            # Additional formatting improvements
            final_output = format_agent_response(final_output)

        # Extract tool calls if any
        tool_calls = []
        if hasattr(result, 'tool_calls') and result.tool_calls:
            tool_calls = result.tool_calls
        elif hasattr(result, 'messages'):
            for message in result.messages:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls.extend(message.tool_calls)

        print(f"DEBUG - Final responding agent: {target_agent_name}")
        print(f"DEBUG - Final output preview: {final_output[:100]}...")

        return {
            "agent": target_agent_name,
            "text": final_output,
            "tool_calls": tool_calls,
            "events": getattr(result, 'events', [])
        }

    except Exception as e:
        print(f"DEBUG - Error running agent: {e}")
        # Fallback response
        return {
            "agent": "Triage Agent",
            "text": f"I'm here to help! How can I assist you with courses, schedules, or campus life?",
            "tool_calls": [],
            "events": []
        }
