from django.urls import path
from .views import ModelSubmissionView, ModelVerificationView

urlpatterns = [
    path('submit/', ModelSubmissionView.as_view(), name='submit_model'),
    path('verify/<int:model_id>/<str:action>/', ModelVerificationView.as_view(), name='verify_model'),
]