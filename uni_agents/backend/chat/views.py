import json
import asyncio
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Session, Message
from .serializers import SessionSerializer, MessageSerializer
from . import agents_integration

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chat(request):
    if request.method == "POST":
        body = json.loads(request.body.decode("utf-8"))
        text = body.get("text")
        session_id = body.get("session_id", "new-session")

        # TODO: plug in triage + agents SDK here
        response = {
            "agent": "Course Advisor",
            "text": f"You asked: {text}. (Example response)",
            "session_id": session_id
        }
        return JsonResponse(response)
    return JsonResponse({"error": "Invalid request"}, status=400)

@api_view(["POST"])
def create_session(request):
    s = Session.objects.create()
    return Response({"session_id": str(s.id)})

@api_view(["POST"])
def post_message(request):
    """
    Request body: { session_id: <uuid>, text: <string> }
    """
    data = request.data
    session_id = data.get("session_id")
    text = data.get("text", "").strip()
    if not text:
        return Response({"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST)

    if session_id:
        session = get_object_or_404(Session, pk=session_id)
    else:
        session = Session.objects.create()

    # store user message
    Message.objects.create(session=session, sender="user", text=text)

    # Build session_messages array for context
    msgs = []
    for m in session.messages.order_by("created_at").all():
        msgs.append({"sender": m.sender, "text": m.text, "meta": m.meta})

    # Run triage & handle (this executes handoffs and tool calls)
    try:
        result = asyncio.run(agents_integration.run_triage_and_handle(session_messages=msgs, user_text=text))
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    agent_name = result.get("agent", "Unknown")
    reply_text = result.get("text", "Sorry, I couldn't produce a response.")

    # Store tool outputs as messages if present
    tool_calls = result.get("tool_calls", [])
    for t in tool_calls:
        Message.objects.create(session=session, sender="tool", text=json.dumps(t))

    # Store agent reply
    Message.objects.create(session=session, sender=agent_name, text=reply_text)

    return Response({
        "session_id": str(session.id),
        "agent": agent_name,
        "text": reply_text
    })

@api_view(["POST"])
def clear_session(request):
    session_id = request.data.get("session_id")
    if session_id:
        try:
            s = Session.objects.get(pk=session_id)
            s.delete()
            # create new session
            ns = Session.objects.create()
            return Response({"session_id": str(ns.id)})
        except Session.DoesNotExist:
            ns = Session.objects.create()
            return Response({"session_id": str(ns.id)})
    else:
        ns = Session.objects.create()
        return Response({"session_id": str(ns.id)})

@api_view(["GET"])
def session_history(request, session_id):
    s = get_object_or_404(Session, pk=session_id)
    messages = []
    for m in s.messages.order_by("created_at").all():
        messages.append({"sender": m.sender, "text": m.text, "meta": m.meta, "created_at": m.created_at})
    return Response({"session_id": str(s.id), "messages": messages})

def index(request):
    """API root endpoint - returns information about available endpoints"""
    api_info = {
        "message": "University Multi-Agent Support API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/session/": "Create a new chat session",
            "POST /api/message/": "Send a message to agents",
            "POST /api/clear/": "Clear chat session",
            "GET /api/history/<session_id>/": "Get session history",
            "POST /api/chat/": "Alternative chat endpoint (compatibility)"
        },
        "frontend_url": "http://localhost:5173",
        "documentation": "See README.md for setup instructions"
    }
    return JsonResponse(api_info)