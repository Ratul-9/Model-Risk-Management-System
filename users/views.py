from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Team

@method_decorator(csrf_exempt, name='dispatch')
class EditorRegistrationView(View):
   
    def post(self, request):
        import json
        data = json.loads(request.body)
        
        selected_team = get_object_or_404(Team, id=data.get('team_id'))
        
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            role=User.EDITOR,
            team=selected_team,
            is_active=False,
            registration_status='PENDING'
        )

        base_url = "http://127.0.0.1:8000/users/decision"
        approve_link = f"{base_url}/{user.unique_id}/approve/"
        reject_link = f"{base_url}/{user.unique_id}/reject/"
        
        send_mail(
            subject="Action Required: New Editor Registration",
            message=f"New Editor {user.username} joined {selected_team.name}.\n\n"
                    f"APPROVE: {approve_link}\n\n"
                    f"REJECT: {reject_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[selected_team.lead_admin.email],
        )

        return JsonResponse({"message": "Registration submitted. Email sent to Admin.", "uid": user.unique_id})

class AdminDecisionView(View):
    def get(self, request, uid, action):
        user = get_object_or_404(User, unique_id=uid)
        
        if action == 'approve':
            user.registration_status = 'APPROVED'
            user.is_active = True
            msg = f"User {user.username} has been APPROVED and activated."
        elif action == 'reject':
            user.registration_status = 'REJECTED'
            user.is_active = False
            msg = f"User {user.username} has been REJECTED."
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)
            
        user.save()
        return JsonResponse({"status": "Success", "message": msg})