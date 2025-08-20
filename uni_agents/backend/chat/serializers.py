from rest_framework import serializers
from .models import Session, Message

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "created_at", "metadata"]

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "session", "sender", "text", "created_at", "meta"]
