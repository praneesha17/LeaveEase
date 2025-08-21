# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'department', 'roll_number', 'role',
            'password1', 'password2'
        ]

from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = [
            'leave_type', 'start_date', 'end_date', 'reason',
            'address_during_leave', 'emergency_contact', 'document'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'address_during_leave': forms.TextInput(attrs={'placeholder': 'Where can you be reached?'}),
            'emergency_contact': forms.TextInput(attrs={'placeholder': 'Emergency contact number'}),
        }
