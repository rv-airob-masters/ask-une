from django.urls import path
from . import views

urlpatterns = [
    path("session/", views.create_session, name="create_session"),
    path("message/", views.post_message, name="post_message"),
    path("clear/", views.clear_session, name="clear_session"),
    path("history/<uuid:session_id>/", views.session_history, name="session_history"),
    path("chat/", views.chat, name="chat"),  # Alternative endpoint for compatibility
    path("", views.index, name="index"),
]
