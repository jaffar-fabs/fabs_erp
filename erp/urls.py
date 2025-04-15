"""
URL configuration for erp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from payroll import views as auth_views
from security import views as role_views
from payroll import views as payroll_views
from payroll import views as projects
from payroll import views
from payroll.views import GradeMasterList
from payroll.views import get_employee_data
from payroll.views import my_login_view, logout
from payroll import views as Holiday
from payroll.views import my_login_view, logout, employee_master,save_employee,dashboard_view,deactivate_employee,check_emp_code
from payroll.views import MenuMaster
from django.conf import settings
from django.conf.urls.static import static
from payroll.context_processors import check_process_cycle




urlpatterns = [
    path('sidebar', dashboard_view),
    path('employee',employee_master,name ='employee_master'),
    path('create_employee/', save_employee, name='create_employee'),
    path('get_employee_details/<int:employee_id>/', views.get_employee_details, name='get_employee_details'),
    path('update_employee/<int:employee_id>/', save_employee, name='update_employee'),
    path('deactivate_employee/<str:employee_id>/', deactivate_employee, name='deactivate_employee'),
    path('after-login/', my_login_view, name='after-login'),
    path('logout/', logout, name='logout'),
    path('index', payroll_views.index, name='index'),
    path('', auth_views.Login.as_view(), name='login'),
    path('users/', auth_views.UserMasterList.as_view(), name='user_list'),
    path('users/create/', auth_views.UserMasterCreate.as_view(), name='user_create'),
    path('users/update/<int:user_master_id>/', auth_views.UserMasterUpdate.as_view(), name='user_update'),
    path('users/delete/<int:user_master_id>/', auth_views.UserMasterDelete.as_view(), name='user_delete'),
    path('get-employee-data/<str:emp_code>/', get_employee_data, name='get_employee_data'),

    #leav Master urls
    path('leavemaster/', views.leave_master_list, name='leavemaster'),
    path('leavemaster/add/', views.create_leave_master, name='create_leavemaster'),
    path('leavemaster/delete/<int:pk>/', views.delete_leavemaster, name='delete_leavemaster'),
    #seed Master urls
    path('create_seed/', views.create_seed, name='create_seed'),
    path('update_seed_status/<int:seed_id>/', views.update_seed_status, name='update_seed_status'),
    path('edit_seed/<int:seed_id>/', views.edit_seed, name='edit_seed'),
    path('get_seed/<int:seed_id>/', views.get_seed, name='get_seed'),

    # Role Master URLs
    path('roles/', role_views.RoleMasterList.as_view(), name='role_list'),
    path('roles/create/', role_views.RoleMasterCreate.as_view(), name='role_create'),
    path('roles/update/<int:role_id>/', role_views.RoleMasterUpdate.as_view(), name='role_update'),
    path('roles/delete/<int:role_id>/', role_views.RoleMasterDelete.as_view(), name='role_delete'),
    #path('admin/', admin.site.urls),
    #path ('', auth_views.Login.as_view(), name='login'),
    path('payroll/paycyle_master',payroll_views.Paycycle.as_view(),name = 'payroll_paycycle_master'),
    path('paycycle/delete/<int:process_cycle_id>/', payroll_views.Paycycle.as_view(), name='delete_paycycle'), 
    path('check-process-cycle/', check_process_cycle, name='check_process_cycle'),

    #project Master


    path('payroll/projects/', projects.project, name='project'),
    path("delete_project/", projects.delete_project, name="delete_project"),
    path('check-project-code/', projects.check_project_code, name='check_project_code'),

    path('payroll/code_master_list/', payroll_views.CodeMasterList.as_view(), name='code_master_list'),
    path('payroll/grade_master/', GradeMasterList.as_view(), name='grade_master'), 

    #Holdday Master

    path('payroll/holiday_list/', views.holidayList, name='holiday_master'),
    path('payroll/holiday_create/', views.holidayCreate, name='holiday_create'),
    path('payroll/holiday_edit/', views.holidayEdit, name='holiday_edit'),
    path('check_holiday/', views.check_holiday, name='check_holiday'),    
    path('payroll/delete_holiday', views.delete_holiday, name='delete_holiday'),    
    
    
    #Menu Master
    path("menu_master/", MenuMaster.as_view(), name="menu_list"),
    path('permission/', payroll_views.permission_view, name='permission'),
    path('check-emp-code/', check_emp_code, name='check_emp_code'),
    path('check_grade_code/', views.check_grade_code, name='check_grade_code'),
    path('get-menu-details/<int:menu_id>/', MenuMaster.as_view(), name='get_menu_details'),
    path('delete_menu/', MenuMaster.delete_menu, name='delete_menu'), 

    # User Role Mapping URLs
    path('user-role-mappings/', role_views.user_role_mapping_list, name='user_role_mapping_list'),
    path('user-role-mappings/create/', role_views.UserRoleMappingCreate.as_view(), name='user_role_mapping_create'),
    path('user-role-mappings/update/<int:mappingid>/', role_views.UserRoleMappingUpdate.as_view(), name='user_role_mapping_update'),
    path('user-role-mappings/delete/<int:mappingid>/', role_views.UserRoleMappingDelete.as_view(), name='user_role_mapping_delete'),


    path('payroll/attendance_upload/', payroll_views.attendance_upload, name='attendance_upload'),
    path('payroll/upload_attendance_data/', payroll_views.upload_attendance_data, name='upload_attendance_data'),
    path('payroll/cancel_attendance_upload/', payroll_views.cancel_attendance_upload, name='cancel_attendance_upload'),

    # Comapny Master
    path('payroll/company_list/', views.company_master, name='company_list'),
    path('payroll/add_company/', views.add_company, name='company_add'),
    path('payroll/edit_company/', views.company_edit, name='company_edit'),
    path('payroll/delete_company/', views.company_delete, name='delete_company'),
    path('payroll/check_company_code/', views.check_company_code, name='check_company_code'),
    path('update_role_menu/', payroll_views.update_role_menu, name='update_role_menu'),
    path('get_menus_by_module/<str:module_id>/', payroll_views.get_menus_by_module, name='get_menus_by_module'),

    # Payroll Processing
    path('payroll/payroll_processing/', payroll_views.payroll_processing, name='payroll_processing'),
    path('payroll/cancel_payroll_processing/', payroll_views.cancel_payroll_processing, name='cancel_payroll_processing'),
    path('payroll/fetch_paymonth/', payroll_views.fetch_paymonth, name='fetch_paymonth'),
    path('payroll/fetch_paymonth_adhoc/', payroll_views.fetch_paymonth_adhoc, name='fetch_paymonth_adhoc'),
    path('fetch_codes/', views.fetch_codes, name='fetch_codes'),
    
    # Advance Master
    path('payroll/advance_master/', views.AdvanceMasterList.as_view(), name='advance_master'),
    path('get-advance-details/<int:advance_id>/', views.get_advance_details, name='get_advance_details'),
    path('update-advance-details/<int:advance_id>/', views.update_advance_details, name='update_advance_details'),
    path('toggle-active-status/<int:advance_id>/', views.toggle_active_status, name='toggle_active_status'),

    # Adhoc Earn Deduct
    path('adhoc-earn-deduct/', views.adhoc_earn_deduct_list, name='adhoc_earn_deduct_list'),
    path('adhoc-earn-deduct/create/', views.create_adhoc_earn_deduct, name='create_adhoc_earn_deduct'),
    path('adhoc-earn-deduct/update/<str:emp_code>/', views.update_adhoc_earn_deduct, name='update_adhoc_earn_deduct'),
    path('adhoc-earn-deduct/delete/<str:emp_code>/', views.delete_adhoc_earn_deduct, name='delete_adhoc_earn_deduct'),

    # Camp Master
    path('camp_master/', views.camp_list, name='camp_master'),
    path('camp_master/create/', views.create_camp, name='create_camp'),
    path('camp_master_edit/', views.camp_master_edit, name='camp_master_edit'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)