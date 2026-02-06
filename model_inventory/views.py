import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.core.mail import EmailMultiAlternatives # Changed for HTML support
from django.utils.html import strip_tags # To create plain-text version
from django.conf import settings
from .models import ModelAsset
from users.models import User, Team

@method_decorator(csrf_exempt, name='dispatch')
class ModelSubmissionView(View):
    def post(self, request):
        data = json.loads(request.body)
        developer = get_object_or_404(User, id=data.get('developer_id'))
        team = developer.team 

        model_obj = ModelAsset.objects.create(
            name=data.get('name'),
            description=data.get('description', 'No description provided'),
            team=team,
            developer=developer,
            model_format=data.get('format'),
            code_path=data.get('code_path'),
            data_path=data.get('data_path'),
            risk_rating=data.get('risk_rating'),
            is_active=False  
        )

        base_url = "http://127.0.0.1:8000/inventory/verify"
        approve_link = f"{base_url}/{model_obj.id}/approve/"
        reject_link = f"{base_url}/{model_obj.id}/reject/"

        # --- HTML Email Content ---
        subject = f"URGENT: Model Validation Required - {model_obj.name}"
        
        # Inline CSS is mandatory because most email clients ignore external/internal <style> tags
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #002d72;">Model Governance Submission</h2>
                <p>A new model asset has been submitted for your approval:</p>
                <div style="background: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                    <p><strong>Model:</strong> {model_obj.name}</p>
                    <p><strong>Developer:</strong> {developer.name}</p>
                    <p><strong>Risk Level:</strong> {model_obj.risk_rating}</p>
                    <p><strong>Git/Code Path:</strong> <code>{model_obj.code_path}</code></p>
                </div>
                <p>Please review the technical specifications and take action below:</p>
                <div style="margin-top: 25px;">
                    <a href="{approve_link}" 
                       style="background-color: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-right: 10px;">
                       APPROVE MODEL
                    </a>
                    
                    <a href="{reject_link}" 
                       style="background-color: #dc3545; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                       REJECT MODEL
                    </a>
                </div>
                <p style="font-size: 11px; color: #777; margin-top: 30px;">
                    Confidential: Internal Bank Use Only.
                </p>
            </body>
        </html>
        """
        
        # Create the plain text alternative for security and older email clients
        text_content = strip_tags(html_content)

        # Create the email object
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[team.lead_admin.email],
        )
        
        # Attach the HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Send it!
        email.send()

        return JsonResponse({
            "status": "Submitted for Validation",
            "model_id": model_obj.id,
            "assigned_checker": team.lead_admin.username
        })

class ModelVerificationView(View):
    def get(self, request, model_id, action):
        model_obj = get_object_or_404(ModelAsset, id=model_id)
        
        if action == 'approve':
            model_obj.is_active = True
            model_obj.save()
            return JsonResponse({"message": f"Model {model_obj.name} is now ACTIVE."})
        
        elif action == 'reject':
            model_obj.delete() 
            return JsonResponse({"message": "Model rejected and removed from inventory."})
        
        return JsonResponse({"error": "Invalid action"}, status=400)