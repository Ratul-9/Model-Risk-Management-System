import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.core.mail import EmailMultiAlternatives # Changed
from django.utils.html import strip_tags # Changed
from django.conf import settings
from .models import User, Team

@method_decorator(csrf_exempt, name='dispatch')
class EditorRegistrationView(View):
    def post(self, request):
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
        
        # --- HTML Email Content with Buttons ---
        subject = "Action Required: New Editor Registration"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #002d72;">New User Access Request</h2>
                <p>A new <strong>Editor</strong> has registered and requires your approval to access the MRM system.</p>
                
                <div style="background-color: #f4f4f4; padding: 15px; border-left: 5px solid #002d72; margin: 20px 0;">
                    <p><strong>Username:</strong> {user.username}</p>
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Assigned Team:</strong> {selected_team.name}</p>
                </div>

                <p>Please authorize or deny this request:</p>
                
                <div style="margin-top: 25px;">
                    <a href="{approve_link}" 
                       style="background-color: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block; margin-right: 10px;">
                       APPROVE USER
                    </a>

                    <a href="{reject_link}" 
                       style="background-color: #dc3545; color: white; padding: 12px 25px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                       REJECT USER
                    </a>
                </div>
                
                <p style="font-size: 11px; color: #999; margin-top: 40px;">
                    This is an automated security notification. Do not share these links.
                </p>
            </body>
        </html>
        """
        
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[selected_team.lead_admin.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return JsonResponse({
            "message": "Registration submitted. Email sent to Team Admin.", 
            "uid": user.unique_id
        })

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