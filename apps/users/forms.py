from django.contrib.auth.forms import AdminUserCreationForm

from .models import User


class CustomUserCreationForm(AdminUserCreationForm):
    """Create Admin users with the same email identity used by the API."""

    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ('email',)

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = user.email
        if commit:
            user.save()
        return user
