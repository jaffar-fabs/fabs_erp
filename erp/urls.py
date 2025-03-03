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
from payroll.views import my_login_view, logout




urlpatterns = [
    path('after-login/', my_login_view, name='after-login'),
    path('logout/', logout, name='logout'),
    path('index', payroll_views.index, name='index'),
    path('', auth_views.Login.as_view(), name='login'),
    path('users/', auth_views.UserMasterList.as_view(), name='user_list'),
    path('users/create/', auth_views.UserMasterCreate.as_view(), name='user_create'),
    path('users/update/<int:user_master_id>/', auth_views.UserMasterUpdate.as_view(), name='user_update'),
    path('users/delete/<int:user_master_id>/', auth_views.UserMasterDelete.as_view(), name='user_delete'),

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
    path('payroll/projects/', projects.project, name='project'),
    path("delete_project/", projects.delete_project, name="delete_project"),
    path('payroll/code_master_list/', payroll_views.CodeMasterList.as_view(), name='code_master_list'),
    path('payroll/grade_master/', GradeMasterList.as_view(), name='grade_master'), 
]