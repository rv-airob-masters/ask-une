#!/usr/bin/env python3
"""
Simple test script to verify the Triage Agent routing logic works correctly.
This script tests the new approach where the Triage Agent handles both routing and conversations.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'uni_agents', 'backend'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from chat.agents_integration import run_triage_and_handle

async def test_routing():
    """Test different types of queries to verify routing works correctly."""
    
    test_cases = [
        # Test 1: Initial course question
        {
            "query": "What courses should I take for computer science?",
            "expected_agent": "Course Advisor",
            "description": "Initial course question - should route to Course Advisor",
            "context": []
        },
        # Test 2: Follow-up question about electives (should stay with Course Advisor)
        {
            "query": "What about electives?",
            "expected_agent": "Course Advisor",
            "description": "Follow-up about electives after course discussion - should stay with Course Advisor",
            "context": [
                {"sender": "user", "text": "What courses should I take for computer science?"},
                {"sender": "Course Advisor", "text": "I recommend CS320 and STAT210 for data science foundations..."}
            ]
        },
        # Test 3: Poetry request (topic change)
        {
            "query": "Write me a haiku about campus life",
            "expected_agent": "University Poet",
            "description": "Poetry request - should route to University Poet regardless of context",
            "context": [
                {"sender": "user", "text": "What courses should I take for computer science?"},
                {"sender": "Course Advisor", "text": "I recommend CS320 and STAT210..."}
            ]
        },
        # Test 4: Follow-up poetry request
        {
            "query": "Write another one about the library",
            "expected_agent": "University Poet",
            "description": "Follow-up poetry request - should stay with University Poet",
            "context": [
                {"sender": "user", "text": "Write me a haiku about campus life"},
                {"sender": "University Poet", "text": "Students gather here\nKnowledge flows like autumn leaves\nWisdom takes its root"}
            ]
        },
        # Test 5: Schedule question
        {
            "query": "When do exams start this semester?",
            "expected_agent": "Scheduling Assistant",
            "description": "Schedule question - should route to Scheduling Assistant",
            "context": []
        },
        # Test 6: Contextual follow-up with pronouns
        {
            "query": "Tell me more about those requirements",
            "expected_agent": "Course Advisor",
            "description": "Contextual follow-up with pronouns - should stay with Course Advisor",
            "context": [
                {"sender": "user", "text": "What are the prerequisites for data science?"},
                {"sender": "Course Advisor", "text": "For data science, you need MATH210, CS250, and STAT210 as prerequisites..."}
            ]
        },
        # Test 7: General greeting
        {
            "query": "Hello, how are you?",
            "expected_agent": "Triage Agent",
            "description": "General greeting - should be handled by Triage Agent",
            "context": []
        }
    ]
    
    print("Testing Triage Agent Routing Logic")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print(f"Expected Agent: {test_case['expected_agent']}")

        # Show context if any
        context = test_case.get('context', [])
        if context:
            print(f"Context: {len(context)} previous messages")
            for j, ctx_msg in enumerate(context):
                print(f"  {j+1}. {ctx_msg['sender']}: {ctx_msg['text'][:50]}...")

        try:
            # Run the query through our system with context
            result = await run_triage_and_handle(context, test_case['query'])
            actual_agent = result.get('agent', 'Unknown')
            response_text = result.get('text', 'No response')

            print(f"Actual Agent: {actual_agent}")
            print(f"Response Preview: {response_text[:100]}...")

            # Check if routing was correct
            if actual_agent == test_case['expected_agent']:
                print("✅ PASS - Correct routing")
            else:
                print("❌ FAIL - Incorrect routing")

        except Exception as e:
            print(f"❌ ERROR - {str(e)}")

        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_routing())
