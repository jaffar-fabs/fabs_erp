from django.urls import path
from . import views

urlpatterns = [
    # ... existing urls ...
    path('attendance-correction/', views.attendance_correction, name='attendance_correction'),
    path('fetch-attendance-data/', views.fetch_attendance_data, name='fetch_attendance_data'),
    path('save-attendance-correction/', views.save_attendance_correction, name='save_attendance_correction'),
    path('get-employee-process-cycle/', views.get_employee_process_cycle, name='get_employee_process_cycle'),
    # ... existing urls ...
] 