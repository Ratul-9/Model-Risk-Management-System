from django.db import models
from users.models import User, Team

class ModelAsset(models.Model):
    RISK_LEVELS = [
        ('HIGH', 'High Risk (Tier 1)'),
        ('MEDIUM', 'Medium Risk (Tier 2)'),
        ('LOW', 'Low Risk (Tier 3)'),
    ]

    FORMAT_CHOICES = [
        ('PYTHON', 'Python Script'),
        ('R', 'R Script'),
        ('CSV', 'Data/CSV'),
        ('CPP', 'C++ Binary'),
        ('XLSX', 'Excel/VBA'),
        ('SAS', 'SAS Base'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='model_assets')
    developer = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='developed_models')

    model_format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    version = models.CharField(max_length=50, default="1.0.0")
    code_path = models.CharField(max_length=500, help_text="Link to Git or Network Path")
    data_path = models.CharField(max_length=500, help_text="Path to training CSV/Database")
    
    risk_rating = models.CharField(max_length=10, choices=RISK_LEVELS, default='MEDIUM')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (v{self.version}) - {self.risk_rating}"
    
class ModelChangeRequest(models.Model):
    STATUS = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    target_model = models.ForeignKey(ModelAsset, on_delete=models.CASCADE, related_name='change_requests')
    proposed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='proposed_changes')

    changes_json = models.JSONField(help_text="Structured description of proposed changes")
    status = models.CharField(max_length=10, choices=STATUS, default='PENDING')
    admin_comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)