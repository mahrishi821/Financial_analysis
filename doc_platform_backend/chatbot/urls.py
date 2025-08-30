from django.urls import path
# from .views import FileUploadView, GenerateReportView
from .views import ChatbotUploadView,ProcessChatbotUploadView, ChatbotQueryView, ChatbotHistoryView, ChatbotUserSessionView

urlpatterns = [
    path("chatbot/upload/", ChatbotUploadView.as_view(), name="chatbot-upload"),
    path("chatbot/process/<int:pk>/", ProcessChatbotUploadView.as_view(), name="chatbot-process"),
    path("chatbot/query/<int:pk>/", ChatbotQueryView.as_view(), name="chatbot-query"),
    path("chatbot/history/<int:pk>/", ChatbotHistoryView.as_view(), name="chatbot-history"),
    path("chatbot/session/",ChatbotUserSessionView.as_view(),name="chatbot-session")
]
