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
        "You are University Poet. You MUST respond ONLY in traditional haiku format: "
        "- Exactly 3 lines "
        "- Line 1: exactly 5 syllables "
        "- Line 2: exactly 7 syllables "
        "- Line 3: exactly 5 syllables "
        "- Topic: campus culture and social life only "
        "- No additional text, explanations, or commentary "
        "- If asked about schedules or courses, refuse in haiku format and suggest the appropriate assistant. "
        "Example format:\n"
        "Students gather here \n"
        "Knowledge flows like autumn leaves \n"
        "Wisdom takes its root "
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

# Router agent - determines which agent should handle the query with conversation context awareness
router_agent = Agent(
    name="Router Agent",
    instructions=(
        "You are the Router Agent. Your ONLY job is to determine which agent should handle a query. "
        "You MUST respond with ONLY the exact agent name - nothing else.\n\n"

        "CRITICAL INSTRUCTION: Your response must be EXACTLY one of these four agent names (copy exactly):\n"
        "Course Advisor\n"
        "University Poet\n"
        "Scheduling Assistant\n"
        "Triage Agent\n\n"

        "DO NOT:\n"
        "- Provide course recommendations\n"
        "- Give any advice or information\n"
        "- Add explanations or additional text\n"
        "- Use brackets, quotes, or formatting\n"
        "- Answer the user's question\n\n"

        "ONLY respond with the agent name that should handle the query.\n\n"

        "ROUTING RULES:\n"
        "- ANY question about courses, classes, academic planning, study, education, majors, degrees, curriculum, credits, prerequisites, electives, subjects, course codes, computer science, data science, AI, machine learning, programming, statistics → Course Advisor\n"
        "- ANY request for haiku, poetry, verses, creative writing about campus → University Poet\n"
        "- ANY question about schedules, dates, times, exams, calendar, deadlines, registration → Scheduling Assistant\n"
        "- General greetings, unclear requests, help requests → Triage Agent\n\n"

        "CONTEXT ANALYSIS: Look at conversation history formatted as '[Agent Name]: response text' to understand what was previously discussed.\n\n"

        "ROUTING PRIORITY:\n"
        "1. If user asks about courses/education/academic topics → Course Advisor\n"
        "2. If user asks for poetry/haiku/creative writing → University Poet\n"
        "3. If user asks about schedules/dates/times → Scheduling Assistant\n"
        "4. If previous specialist agent responded and current query is a follow-up → same specialist\n"
        "5. If general greeting or unclear → Triage Agent\n\n"

        "FOLLOW-UP DETECTION:\n"
        "If you see '[Course Advisor]:' in recent history and user asks 'what about', 'tell me more', 'also', 'and', 'electives', 'prerequisites' → Course Advisor\n"
        "If you see '[University Poet]:' in recent history and user asks 'write another', 'more poetry', 'another one' → University Poet\n"
        "If you see '[Scheduling Assistant]:' in recent history and user asks 'when do', 'what about deadlines' → Scheduling Assistant\n\n"

        "EXAMPLES (respond with ONLY the agent name):\n"
        "User: 'What courses should I take for data science?' → Course Advisor\n"
        "User: 'undergrad in ML' (after course discussion) → Course Advisor\n"
        "User: 'What about electives?' (after course discussion) → Course Advisor\n"
        "User: 'Write me a haiku' → University Poet\n"
        "User: 'Write another one' (after poetry) → University Poet\n"
        "User: 'When do exams start?' → Scheduling Assistant\n"
        "User: 'Hello' → Triage Agent\n\n"

        "REMEMBER: Respond with ONLY the agent name. No explanations, no course advice, no additional text."
    ),
    tools=[],
    model="gpt-4o-mini",
)

# Triage agent - handles general conversations and unclear requests
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are the Triage Agent. You handle general greetings, unclear requests, and provide guidance when users need help. "
        "You are friendly, helpful, and conversational. When users greet you or ask general questions, engage naturally. "
        "If users ask about specific topics that other agents handle, politely guide them:\n"
        "- For course questions: 'I can help you find the right courses! What subject or level are you interested in?'\n"
        "- For schedule questions: 'I can help you with scheduling information! What dates or deadlines do you need to know about?'\n"
        "- For creative requests: 'I can help with campus poetry! Would you like a haiku about university life?'\n\n"
        "Keep responses conversational and helpful. Ask follow-up questions to better understand what the user needs."
    ),
    tools=[],
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
    Priority: 1) Strong agent keywords, 2) Follow-up context, 3) Default to Triage
    """
    user_lower = user_text.lower()
    
    print(f"DEBUG - Routing analysis for: '{user_text}'")
    
    # FIRST PRIORITY: Check for strong agent-specific indicators
    
    # Poetry requests (University Poet) - highest specificity
    poetry_indicators = ['haiku', 'poem', 'poetry', 'verse', 'write me a', 'compose a']
    if any(indicator in user_lower for indicator in poetry_indicators):
        print(f"DEBUG - Poetry request detected, routing to: University Poet")
        return "University Poet"
    
    # Course-related queries (Course Advisor)
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
    
    # Schedule-related queries (Scheduling Assistant)
    schedule_keywords = [
        'schedule', 'time', 'exam', 'exams', 'calendar', 'date', 'dates', 'when', 
        'semester', 'deadline', 'deadlines', 'final', 'finals', 'midterm', 'midterms',
        'start', 'end', 'begins', 'registration', 'when do', 'when does', 'when is'
    ]
    if any(keyword in user_lower for keyword in schedule_keywords):
        print(f"DEBUG - Schedule query detected, routing to: Scheduling Assistant")
        return "Scheduling Assistant"
    
    # SECOND PRIORITY: Check conversation context for follow-up questions
    # (Only if no strong agent-specific keywords were found above)
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
    
    # THIRD PRIORITY: Default to Triage Agent for general queries
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
    Use Router Agent to determine routing, then call the appropriate agent directly.
    Returns: { 'agent': agent_name, 'text': ..., 'tool_calls': [...], 'events': [...] }
    """
    # Convert session messages for Router Agent (with agent context for routing decisions)
    router_conversation_history = []
    if session_messages:
        for msg in session_messages[:-1]:  # exclude the current user message
            if msg['sender'] == 'user':
                router_conversation_history.append({"role": "user", "content": msg['text']})
            elif msg['sender'] not in ['tool']:  # agent messages
                # Include agent name in the content for Router Agent context
                agent_context = f"[{msg['sender']}]: {msg['text']}"
                router_conversation_history.append({"role": "assistant", "content": agent_context})

    # Router Agent input with context
    router_input_messages = router_conversation_history + [{"role": "user", "content": user_text}]

    # Convert session messages for actual agent execution (without agent prefixes)
    agent_conversation_history = []
    if session_messages:
        for msg in session_messages[:-1]:  # exclude the current user message
            if msg['sender'] == 'user':
                agent_conversation_history.append({"role": "user", "content": msg['text']})
            elif msg['sender'] not in ['tool']:  # agent messages
                # No agent prefix for actual agent execution
                agent_conversation_history.append({"role": "assistant", "content": msg['text']})

    # Agent execution input without prefixes
    agent_input_messages = agent_conversation_history + [{"role": "user", "content": user_text}]

    # Debug: Print conversation context for Router Agent
    print(f"DEBUG - Conversation context for Router Agent:")
    for i, msg in enumerate(router_input_messages):
        content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"  {i+1}. {msg['role']}: {content_preview}")

    try:
        # Step 1: Use Router Agent to determine which agent should handle this
        print(f"DEBUG - Running Router Agent to determine routing for: '{user_text}'")
        router_result = await runner.run(router_agent, router_input_messages)

        # Extract the routing decision
        routing_decision = router_result.final_output if hasattr(router_result, 'final_output') else str(router_result)
        if isinstance(routing_decision, str):
            routing_decision = routing_decision.strip().strip('"\'')
            # Remove brackets if Router Agent added them
            routing_decision = routing_decision.strip('[]')

            # If the response is too long, it means Router Agent gave advice instead of just agent name
            # Extract just the agent name from the beginning
            if len(routing_decision) > 50:  # Agent names should be short
                print(f"DEBUG - Router Agent gave long response instead of agent name, extracting...")
                # Look for agent names at the start of the response
                for agent_name in ["Course Advisor", "University Poet", "Scheduling Assistant", "Triage Agent"]:
                    if routing_decision.startswith(agent_name):
                        routing_decision = agent_name
                        break
                else:
                    # If no agent name found at start, default based on content
                    if any(word in routing_decision.lower() for word in ['course', 'class', 'study', 'academic', 'machine learning', 'data science']):
                        routing_decision = "Course Advisor"
                    elif any(word in routing_decision.lower() for word in ['haiku', 'poem', 'poetry']):
                        routing_decision = "University Poet"
                    elif any(word in routing_decision.lower() for word in ['schedule', 'exam', 'calendar']):
                        routing_decision = "Scheduling Assistant"
                    else:
                        routing_decision = "Triage Agent"

        print(f"DEBUG - Router Agent raw decision: '{router_result.final_output if hasattr(router_result, 'final_output') else str(router_result)}'")
        print(f"DEBUG - Router Agent cleaned decision: '{routing_decision}'")

        # Step 2: Get the appropriate agent based on routing decision
        agent_mapping = {
            "Course Advisor": course_advisor_agent,
            "University Poet": university_poet_agent,
            "Scheduling Assistant": scheduling_agent,
            "Triage Agent": triage_agent
        }

        target_agent = agent_mapping.get(routing_decision, triage_agent)
        target_agent_name = routing_decision if routing_decision in agent_mapping else "Triage Agent"

        print(f"DEBUG - Selected agent: {target_agent_name}")

        # Step 3: Run the selected agent (using clean conversation history without agent prefixes)
        print(f"DEBUG - Running {target_agent_name} with clean conversation history")
        print(f"DEBUG - Clean conversation context for {target_agent_name}:")
        for i, msg in enumerate(agent_input_messages):
            content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"  {i+1}. {msg['role']}: {content_preview}")

        result = await runner.run(target_agent, agent_input_messages)

        # Extract the final output
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
        print(f"DEBUG - Error in triage and handle: {e}")
        # Fallback to keyword-based routing
        target_agent_name = determine_target_agent(user_text, session_messages)

        # Get the appropriate agent
        agent_mapping = {
            "Course Advisor": course_advisor_agent,
            "University Poet": university_poet_agent,
            "Scheduling Assistant": scheduling_agent,
            "Triage Agent": triage_agent
        }

        target_agent = agent_mapping.get(target_agent_name, triage_agent)

        try:
            result = await runner.run(target_agent, agent_input_messages)
            final_output = result.final_output if hasattr(result, 'final_output') else str(result)

            return {
                "agent": target_agent_name,
                "text": final_output,
                "tool_calls": [],
                "events": []
            }
        except:
            return {
                "agent": "Triage Agent",
                "text": f"I'm here to help! How can I assist you with courses, schedules, or campus life?",
                "tool_calls": [],
                "events": []
            }
