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
from auth import views as auth_views
from payroll import views as payroll_views

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path ('', auth_views.Login.as_view(), name='login'),
    path('',payroll_views.Paycycle.as_view(),name = 'payroll_paycycle_master'),
    path('paycycle/delete/<int:process_cycle_id>/', payroll_views.Paycycle.as_view(), name='delete_paycycle'), 

]
