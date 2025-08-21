import calendar

from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from .forms import RegistrationForm, LeaveRequestForm
from .models import LeaveRequest, LeaveBalance, CustomUser, Department
from datetime import timedelta
import json
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.utils.timezone import now

User = get_user_model()

# ------------------- Authentication -------------------

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None and user.role == role.lower():
            login(request, user)
            return redirect(f"{user.role}_dashboard")
        else:
            messages.error(request, "Invalid credentials or role")
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

# ------------------- Student Dashboard -------------------

@login_required
def student_dashboard(request):
    user = request.user
    balance, _ = LeaveBalance.objects.get_or_create(user=user)
    approved_leaves = LeaveRequest.objects.filter(user=user, status='Approved')

    leave_data = []
    for lt in ['Casual Leave', 'Medical Leave', 'Emergency Leave', 'Academic Leave']:
        used = sum(l.duration for l in approved_leaves if l.leave_type == lt)
        remaining = getattr(balance, lt.split()[0].lower(), 0)
        leave_data.append((lt, used, remaining))

    context = {
        'leave_data': leave_data,
        'recent_leaves': LeaveRequest.objects.filter(user=user).order_by('-submitted_at')[:5],
        'total_requests': LeaveRequest.objects.filter(user=user).count(),
        'approved_requests': approved_leaves.count(),
        'pending_requests': LeaveRequest.objects.filter(user=user, status='Pending').count(),
        'rejected_requests': LeaveRequest.objects.filter(user=user, status='Rejected').count(),
    }
    return render(request, 'student/student_dashboard.html', context)

# ------------------- Faculty Dashboard -------------------

@login_required
def faculty_dashboard(request):
    user = request.user
    all_requests = LeaveRequest.objects.filter(user__department=user.department)
    leave_requests = all_requests.filter(status='Pending') if request.GET.get('tab') != 'all' else all_requests

    context = {
        'user': user,
        'pending_count': all_requests.filter(status='Pending').count(),
        'approved_count': all_requests.filter(status='Approved').count(),
        'rejected_count': all_requests.filter(status='Rejected').count(),
        'student_count': CustomUser.objects.filter(role='student', department=user.department).count(),
        'leave_requests': leave_requests,
        'all_requests': all_requests,
        'active_tab': request.GET.get('tab', 'pending')
    }
    return render(request, 'accounts/faculty_dashboard.html', context)

# ------------------- Admin Dashboard & Tabs -------------------

def get_approval_rate():
    total = LeaveRequest.objects.count()
    approved = LeaveRequest.objects.filter(status="Approved").count()
    return round((approved / total) * 100, 2) if total else 0

def get_avg_processing_time():
    processed = LeaveRequest.objects.filter(status__in=['Approved', 'Rejected'], submitted_at__isnull=False)
    avg_duration = processed.annotate(
        duration=ExpressionWrapper(
            F('submitted_at') - F('submitted_at'),
            output_field=DurationField()
        )
    ).aggregate(avg=Avg('duration'))['avg']

    if avg_duration:
        return f"{round(avg_duration.total_seconds() / 86400, 1)}d"
    else:
        return "N/A"

def get_analytics_data():
    pending = LeaveRequest.objects.filter(status="Pending").count()
    approved = LeaveRequest.objects.filter(status="Approved").count()
    rejected = LeaveRequest.objects.filter(status="Rejected").count()

    return {
        'pending_count': pending,
        'approved_count': approved,
        'rejected_count': rejected
    }

def get_department_data():
    departments = Department.objects.all()
    data = []

    for dept in departments:
        users = CustomUser.objects.filter(department=dept)
        students = users.filter(role='student').count()
        faculty = users.filter(role='faculty').count()

        requests = LeaveRequest.objects.filter(user__department=dept)
        total_requests = requests.count()
        approved = requests.filter(status="Approved").count()
        rejected = requests.filter(status="Rejected").count()
        pending = requests.filter(status="Pending").count()

        approval_rate = round((approved / total_requests) * 100, 2) if total_requests else 0

        data.append({
            'name': dept.name,
            'user_count': students + faculty,
            'students': students,
            'faculty': faculty,
            'total': total_requests,
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
            'approval_rate': approval_rate,
        })

    return { 'departments': data }

@login_required



def admin_dashboard(request):
    tab = request.GET.get('tab', 'analytics')
    context = {'tab': tab}

    if tab == 'analytics':
        total_users = CustomUser.objects.count()
        total_requests = LeaveRequest.objects.count()
        pending_requests = LeaveRequest.objects.filter(status='Pending').count()
        approved_requests = LeaveRequest.objects.filter(status='Approved').count()
        approval_rate = (approved_requests / total_requests * 100) if total_requests > 0 else 0

        # Leave requests per month
        monthly_data = (
            LeaveRequest.objects
            .annotate(month=TruncMonth('start_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        months = [calendar.month_name[d['month'].month] for d in monthly_data]
        monthly_counts = [d['count'] for d in monthly_data]

        # Leave distribution
        type_data = LeaveRequest.objects.values('leave_type').annotate(count=Count('id'))
        leave_labels = [d['leave_type'] for d in type_data]
        leave_counts = [d['count'] for d in type_data]

        context.update({
            'total_users': total_users,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approval_rate': round(approval_rate, 1),
            'months': months,
            'monthly_counts': monthly_counts,
            'leave_labels': leave_labels,
            'leave_counts': leave_counts,
        })


    elif tab == 'requests':

        leave_requests = LeaveRequest.objects.select_related('user').order_by('-submitted_at')

        context['leave_requests'] = leave_requests

    elif tab == 'settings':

        default_policies = LeaveBalance._meta.get_fields()

        policies = {

            'Casual Leave': LeaveBalance._meta.get_field('casual').default,

            'Medical Leave': LeaveBalance._meta.get_field('medical').default,

            'Emergency Leave': LeaveBalance._meta.get_field('emergency').default,

            'Academic Leave': LeaveBalance._meta.get_field('academic').default,

        }

        context['policies'] = policies

    return render(request, 'accounts/admin_dashboard.html', context)




@login_required
def all_requests_view(request):
    return render(request, 'admin/all_requests.html', {
        'requests': LeaveRequest.objects.all(),
        'active_tab': 'requests'
    })

@login_required
def admin_settings(request):
    return render(request, 'admin/settings.html', {'active_tab': 'settings'})

# ------------------- Leave Handling -------------------

@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()
            return redirect('student_dashboard')
    else:
        form = LeaveRequestForm()
    return render(request, 'student/apply_leave.html', {'form': form})

@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    return render(request, 'accounts/leave_detail.html', {'leave': leave})

@login_required
def approve_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if leave.status == 'Pending':
        balance, _ = LeaveBalance.objects.get_or_create(user=leave.user)
        if leave.leave_type == "Casual Leave" and balance.casual >= leave.duration:
            balance.casual -= leave.duration
        elif leave.leave_type == "Medical Leave" and balance.medical >= leave.duration:
            balance.medical -= leave.duration
        elif leave.leave_type == "Emergency Leave" and balance.emergency >= leave.duration:
            balance.emergency -= leave.duration
        elif leave.leave_type == "Academic Leave" and balance.academic >= leave.duration:
            balance.academic -= leave.duration
        balance.save()
        leave.status = "Approved"
        leave.save()
    return redirect('faculty_dashboard')

@login_required
def reject_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = 'Rejected'
    leave.save()
    return redirect('faculty_dashboard')
def get_leave_policy_data():
    # Extract defaults from LeaveBalance model
    return {
        'policies': [
            {'type': 'Casual Leave', 'days': LeaveBalance._meta.get_field('casual').default},
            {'type': 'Medical Leave', 'days': LeaveBalance._meta.get_field('medical').default},
            {'type': 'Emergency Leave', 'days': LeaveBalance._meta.get_field('emergency').default},
            {'type': 'Academic Leave', 'days': LeaveBalance._meta.get_field('academic').default},
        ]
    }
