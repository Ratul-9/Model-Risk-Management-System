from django.contrib.auth.models import AbstractUser
from django.db import models

def generateUniqueId():
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=11))


class Team(models.Model):
    name=models.CharField(max_length=255, unique=True)
    lead_admin = models.ForeignKey('User', on_delete=models.PROTECT, null=True, blank=True, related_name='led_teams',limit_choices_to={'role': 'ADMIN'})
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Team {self.name} (Lead: {self.lead_admin.username})"

class User(AbstractUser):
    ADMINISTRATOR = 'ADMIN'
    EDITOR = 'EDITOR'
    VIEWER = 'VIEWER'

    ROLE_CHOICES = [
        (ADMINISTRATOR, 'Administrator'),
        (EDITOR, 'Editor'),
        (VIEWER, 'Viewer'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    registration_status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    unique_id = models.CharField(max_length=11, unique=True, default=generateUniqueId)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=VIEWER)
    name = models.CharField(max_length=255, blank=False)  

    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    