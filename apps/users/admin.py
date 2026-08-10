from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailOTP


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_staff',
        'assigned_doctor',
        'is_available',
        'last_activity',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_available')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'dob')
        }),
        ('Role & Status', {
            'fields': ('role', 'specialization', 'is_available', 'assigned_doctor', 'last_activity')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'role',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

    readonly_fields = ('last_activity', 'last_login', 'date_joined')

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'verified', 'attempts')
    list_filter = ('verified', 'created_at')
    search_fields = ('user__email', 'code')


admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailOTP, EmailOTPAdmin)
