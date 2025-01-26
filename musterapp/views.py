
# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
# from django.urls import reverse

class CustomLoginView(LoginView):
    template_name = 'login.html' 
    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        login(self.request, user)

        if user.role == 'Employee':
            return redirect('employee_dashboard')
        elif user.role == 'Manager':
            return redirect('manager_dashboard')
        elif user.role == 'HR':
            return redirect('hr_dashboard')
        else:
            return redirect('home')  
        

from django.utils import timezone
from .models import Attendance
from django.core.exceptions import PermissionDenied
from django.contrib import messages


@login_required
def clock_in(request):
    if request.user.role != 'Employee':
        raise PermissionDenied
    
    
    
    today = timezone.localdate()  

    # Check if the user already clocked in today
    today_record = Attendance.objects.filter(employee=request.user, date=today).first()
    if today_record and today_record.clock_in:
        messages.info(request, "You have already clocked in today.")

        return redirect('employee_dashboard')
     
    # If no clock-in record exists, create one
    if not today_record:
        today_record = Attendance(employee=request.user, clock_in=timezone.localtime(timezone.now()))
        today_record.save()
        print(f"New attendance created: {today_record}")

    return redirect('employee_dashboard')




@login_required
def clock_out(request):
    if request.user.role != 'Employee':
        raise PermissionDenied

    # Get today's attendance record in IST
    today = timezone.localdate()
    today_record = Attendance.objects.filter(employee=request.user, date=today).first()

    if not today_record:
        messages.error(request, "You need to clock in first before clocking out.")
        return redirect('employee_dashboard')

    if today_record.clock_in and not today_record.clock_out:
        today_record.clock_out = timezone.localtime(timezone.now())  
        today_record.save()
    else:
        messages.error(request, "You have already clocked out today.")
        return redirect('employee_dashboard')

    return redirect('employee_dashboard')


from django.contrib.auth import get_user_model
from datetime import datetime

def manager_dashboard(request):
    if request.user.role != 'Manager':
        raise PermissionDenied
    
    # Fetch all employees for the dropdown (CustomUser model)
    employees = get_user_model().objects.filter(role='Employee')

    # Get the selected employee_id and month from GET parameters
    selected_employee_id = request.GET.get('employee_id', None)
    selected_month = request.GET.get('month', None)

    # Filter attendance records based on employee_id and month
    if selected_employee_id and selected_month:
        attendances = Attendance.objects.filter(
            employee__employee_id=selected_employee_id,
            date__month=selected_month
        )
    elif selected_employee_id:
        attendances = Attendance.objects.filter(employee__employee_id=selected_employee_id)
    elif selected_month:
        attendances = Attendance.objects.filter(date__month=selected_month)
    else:
        attendances = Attendance.objects.all()  

    return render(request, 'manager_dashboard.html', {
        'attendances': attendances,
        'employees': employees,
        'selected_employee_id': selected_employee_id,
        'selected_month': selected_month,
    })



@login_required
def employee_dashboard(request):
    if request.user.role != 'Employee':
        raise PermissionDenied
    # Get attendance record of the employee for today
    today = timezone.localdate()  

    today_record = Attendance.objects.filter(employee=request.user, date=today).first()

    return render(request, 'employee_dashboard.html', {'attendance': today_record})


from django.contrib.auth.hashers import check_password
from .forms import PasswordResetForm
from .models import CustomUser

def reset_password(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data["employee_id"]
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["new_password"]

            try:
                # Get the user based on the employee_id
                user = CustomUser.objects.get(employee_id=employee_id)
                
                if check_password(old_password, user.password):
                    # Password is correct, now update it to the new password
                    user.set_password(new_password)
                    user.save()

                    messages.success(request, "Your password has been reset successfully!")
                    return redirect("login")  
                else:
                    messages.error(request, "The old password you entered is incorrect.")
            except CustomUser.DoesNotExist:
                messages.error(request, "Employee ID does not exist.")
    else:
        form = PasswordResetForm()

    return render(request, "reset_password.html", {"form": form})
