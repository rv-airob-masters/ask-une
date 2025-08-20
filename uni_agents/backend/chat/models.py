import uuid
from django.db import models

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

class Message(models.Model):
    session = models.ForeignKey(Session, related_name="messages", on_delete=models.CASCADE)
    sender = models.CharField(max_length=128)  # 'user', 'Triage Agent', 'Course Advisor', etc
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict, blank=True)
