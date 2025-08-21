from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- User model ---
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    ]
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


# --- Constants ---
LEAVE_TYPES = [
    ('Casual Leave', 'Casual Leave'),
    ('Medical Leave', 'Medical Leave'),
    ('Emergency Leave', 'Emergency Leave'),
    ('Academic Leave', 'Academic Leave'),
]
LEAVE_STATUS = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
]


# --- Leave Request Model ---
class LeaveRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    address_during_leave = models.CharField(max_length=255, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    document = models.FileField(upload_to='leave_documents/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.start_date} to {self.end_date})"

    @property
    def duration(self):
        return (self.end_date - self.start_date).days + 1


# --- Leave Balance Model ---
class LeaveBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    casual = models.IntegerField(default=12)
    medical = models.IntegerField(default=10)
    emergency = models.IntegerField(default=5)
    academic = models.IntegerField(default=8)

    def __str__(self):
        return f"{self.user.username} - Balance"
# accounts/models.py

from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
