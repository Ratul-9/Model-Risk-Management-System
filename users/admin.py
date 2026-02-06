from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Team

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'role', 'team', 'unique_id', 'is_staff')
    
    list_filter = ('role', 'team', 'is_staff', 'is_superuser')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Bank-Specific Metadata', {'fields': ('role', 'unique_id', 'name')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Bank-Specific Metadata', {'fields': ('role', 'name', 'email')}),
    )

    readonly_fields = ('unique_id',)

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'lead_admin', 'description')
    search_fields = ('name', 'lead_admin__username')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Team, TeamAdmin)