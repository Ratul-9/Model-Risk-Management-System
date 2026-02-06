from django.urls import path
from .views import EditorRegistrationView, AdminDecisionView

urlpatterns = [
    path('register/', EditorRegistrationView.as_view(), name='postman_register'),
    path('decision/<str:uid>/<str:action>/', AdminDecisionView.as_view(), name='admin_decision'),
]