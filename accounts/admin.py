# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PremierLeagueReferee

class PremierLeagueRefereeInline(admin.StackedInline):
    model = PremierLeagueReferee
    can_delete = False
    verbose_name_plural = 'Premier League Statistics'
    fk_name = 'user'
    
    def get_queryset(self, request):
        # Only show for users who are referees
        return super().get_queryset(request).filter(user__user_type='referee')


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'profile_picture_approved', 'is_approved', 'is_banned')
    
    # Allow admins to approve profile pictures directly from the list view
    list_editable = ('profile_picture_approved', 'is_banned')

    # Add custom fields to fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': (
                'user_type', 
                'fa_certificate_id', 
                'bio', 
                'profile_picture', 
                'profile_picture_approved',
                'is_approved',
                'is_banned'
            )
        }),
    )
    
    # Adds custom fields to add form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': (
                'user_type', 
                'fa_certificate_id', 
                'bio', 
                'profile_picture', 
                'profile_picture_approved',
                'is_approved',  
                'is_banned'
            )
        }),
        ('Ban Information', {
            'fields': ('is_banned', 'ban_reason', 'ban_until'),
            'classes': ('collapse',),
        }),        
    )

   
    list_filter = ('user_type', 'is_approved', 'profile_picture_approved', 'is_banned')

    # Custom actions for approving profile pictures and users
    actions = ['approve_picture', 'approve_referees', 'ban_users', 'unban_users']

    def ban_users(self, request, queryset):
        queryset.update(is_banned=True)
    ban_users.short_description = "Temporarily ban selected users"
    
    def unban_users(self, request, queryset):
        queryset.update(is_banned=False, ban_reason=None, ban_until=None)
    unban_users.short_description = "Remove ban from selected users"

    def approve_picture(self, request, queryset):
        queryset.update(profile_picture_approved=True)
    approve_picture.short_description = "Approve selected profile pictures"

    def approve_referees(self, request, queryset):
        # Only approves users with user_type 'referee'
        queryset.filter(user_type='referee').update(is_approved=True)
    approve_referees.short_description = "Approve selected referees"

    # Overrides get_queryset to only show is_approved for referees
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show is_approved for referees
        if request.user.is_superuser:
            return qs
        return qs.filter(user_type='referee')

    # Overrides the form to only show is_approved for referees
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.user_type != 'referee':
            # Remove is_approved for non-referees
            fieldsets = list(fieldsets)
            for i, fieldset in enumerate(fieldsets):
                if fieldset[0] == 'Custom Fields':
                    fields = list(fieldset[1]['fields'])
                    if 'is_approved' in fields:
                        fields.remove('is_approved')
                    fieldsets[i] = (fieldset[0], {'fields': fields})
        return fieldsets
    
    def get_inline_instances(self, request, obj=None):
        # Only shows Premier League stats inline for referee users
        if not obj or obj.user_type != 'referee':
            return []
        return super().get_inline_instances(request, obj)

@admin.register(PremierLeagueReferee)
class PremierLeagueRefereeAdmin(admin.ModelAdmin):
    list_display = ('get_referee_name', 'games_officiated', 'yellow_cards', 'red_cards', 
                    'penalties_given', 'performance_rating', 'poor_decisions', 'current_season')
    list_filter = ('current_season', 'user__is_current_referee')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('poor_decisions', '-performance_rating')

    def get_referee_name(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    get_referee_name.short_description = 'Referee'
    
    def get_queryset(self, request):
        # Only shows stats for approved referees
        return super().get_queryset(request).filter(
            user__user_type='referee',
            user__is_approved=True
        )

# Registers the CustomUser model with the updated admin class
admin.site.register(CustomUser, CustomUserAdmin)