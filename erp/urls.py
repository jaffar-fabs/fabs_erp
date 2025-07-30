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
from procurement import views as procurement
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
    path('get_employee_details/', views.get_employee_details, name='get_employee_details'),
    path('update_employee/<int:employee_id>/', save_employee, name='update_employee'),
    path('deactivate_employee/<str:employee_id>/', deactivate_employee, name='deactivate_employee'),
    path('after-login/', my_login_view, name='after-login'),
    path('logout/', logout, name='logout'),
    path('index', payroll_views.index, name='index'),
    path('payroll_dashboard', payroll_views.payroll_dashboard, name='payroll_dashboard'),
    path('hr_metrics_dashboard/', payroll_views.hr_metrics_dashboard, name='hr_metrics_dashboard'),
    path('', auth_views.Login.as_view(), name='login'),
    path('users/', auth_views.UserMasterList.as_view(), name='user_list'),
    path('users/create/', auth_views.UserMasterCreate.as_view(), name='user_create'),
    path('users/update/<int:user_master_id>/', auth_views.UserMasterUpdate.as_view(), name='user_update'),
    path('users/delete/<int:user_master_id>/', auth_views.UserMasterDelete.as_view(), name='user_delete'),
    path('get-employee-data/<str:emp_code>/', get_employee_data, name='get_employee_data'),
    path('check-user-companies/', views.check_user_companies, name='check_user_companies'),

    #leave transaction urls
    path('leave_transaction/', views.leave_transaction_list, name='leave_transaction'),
    path('leave_transaction/add/', views.leave_transaction_add, name='leave_transaction_add'),
    path('leave_transaction/edit/', views.leave_transaction_edit, name='leave_transaction_edit'),
    path('leave_transaction/delete/', views.leave_transaction_delete, name='leave_transaction_delete'),
    path('leave_approval/', views.leave_approval_list, name='leave_approval_list'),
    path('leave_approval/submit/', views.leave_approval, name='leave_approval'),
    

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
    path('get_project_locations/', views.get_project_locations, name='get_project_locations'),
    path('download_project_template/', projects.download_project_template, name='download_project_template'),

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
    path('check-camp-code/', views.check_camp_code, name='check_camp_code'),
    path('fetch-room-numbers/', views.fetch_room_numbers, name='fetch_room_numbers'),
    path('check-employee-allocation/', views.check_employee_allocation, name='check_employee_allocation'),

    #party master
    path('party-master/', views.party_master_list, name='party_master_list'),
    path('create-party/', views.create_party, name='create_party'),
    path('party_master_edit/', views.party_master_edit, name='party_master_edit'),
    path('delete-party/<int:party_id>/', views.delete_party, name='delete_party'),
    path('download_party_template/', views.download_party_template, name='download_party_template'),

    #Camp Allocation
    path('camp_allocation/', views.camp_allocation_list, name='camp_allocation_list'),
    path('camp_allocation/create/', views.camp_allocation_create, name='camp_allocation_create'),
    # path('camp_allocation/edit/', views.camp_allocation_edit, name='camp_allocation_edit'),
    path('check_employee_allocation/', views.check_employee_allocation, name='check_employee_allocation'),
    path('fetch_buildings/', views.fetch_buildings, name='fetch_buildings'),
    path('fetch_floors/', views.fetch_floors, name='fetch_floors'),
    path('fetch_rooms/', views.fetch_rooms, name='fetch_rooms'),
    path('fetch_beds/', views.fetch_beds, name='fetch_beds'),
    path('check_bed_allocation/', views.check_bed_allocation, name='check_bed_allocation'),
    path('camp_transaction_approval/', views.camp_transaction_approval, name='camp_transaction_approval'),
    path('camp_transaction_approval_submit/', views.camp_transaction_approval_submit, name='camp_transaction_approval_submit'),

    #Attendance Correction
    path('attendance_correction/', views.attendance_correction, name='attendance_correction'),
    path('fetch_attendance_data/', views.fetch_attendance_data, name='fetch_attendance_data'),
    path('save_attendance_correction/', views.save_attendance_correction, name='save_attendance_correction'),
    path('get_employee_process_cycle/', views.get_employee_process_cycle, name='get_employee_process_cycle'),

    #Gratuity
    path('gratuity_list/', views.gratuity_list, name='gratuity_list'),
    path('add_gratuity/', views.add_gratuity, name='add_gratuity'),
    path('get_gratuity_details/', views.get_gratuity_details, name='get_gratuity_details'),
    path('update_gratuity/', views.update_gratuity, name='update_gratuity'),
    path('delete_gratuity/', views.delete_gratuity, name='delete_gratuity'),
    path('get_emp_code/', views.get_emp_code, name='get_emp_code'),

    #Leave Master
    path('leave_master/', views.leave_master_list, name='leave_master_list'),
    path('leave_master/create/', views.leave_master_create, name='leave_master_create'),
    path('check_leave_code/', views.check_leave_code, name='check_leave_code'),
    path('get_leave_details/', views.get_leave_details, name='get_leave_details'),
    path('update_leave_details/', views.update_leave_details, name='update_leave_details'),
    path('delete_leave_type/', views.delete_leave_type, name='delete_leave_type'),
    path('get_leave_master_details/', views.get_leave_master_details, name='get_leave_master_details'),
    path('check_leave_exists/', views.check_leave_exists, name='check_leave_exists'),

    #Rejoin Approval
    path('rejoin_approval/', views.rejoin_approval_list, name='rejoin_approval_list'),
    path('get_rejoin_details/', views.get_rejoin_details, name='get_rejoin_details'),
    path('rejoin_approval_submit/', views.rejoin_approval_submit, name='rejoin_approval_submit'),
    path('get-rejoin-notifications/', views.get_rejoin_notifications, name='get_rejoin_notifications'),

    #Recruitment
    path('ao_entry/', views.ao_entry_list, name='ao_entry_list'),
    path('ao_entry/create/', views.ao_entry_create, name='ao_entry_create'),
    path('ao_entry/edit/', views.ao_entry_edit, name='ao_entry_edit'),
    path('ao_entry/update/', views.ao_entry_update, name='ao_entry_update'),
    path('ao_entry/delete/', views.ao_entry_delete, name='ao_entry_delete'),
    path('recruitment_list/', views.recruitment_list, name='recruitment_list'),
    path('recruitment_update/', views.recruitment_update, name='recruitment_update'),
    path('recruitment_edit/', views.recruitment_edit, name='recruitment_edit'),
    path('recruitment/convert-to-employee/', views.convert_to_employee, name='convert_to_employee'),

    #MRF
    path('mrf_list/', views.mrf_list, name='mrf_list'),
    path('create_mrf/', views.create_mrf, name='create_mrf'),
    path('edit_mrf/', views.edit_mrf, name='edit_mrf'),
    path('delete_mrf/', views.delete_mrf, name='delete_mrf'),
    path('get_mrf_details/', views.get_mrf_details, name='get_mrf_details'),
    path('get_mrf_details_for_ao/', views.get_mrf_details_for_ao, name='get_mrf_details_for_ao'),

    #Employee PP
    path('employee_pp/', views.employee_pp_list, name='employee_pp_list'),
    path('employee_pp/create/', views.employee_pp_create, name='employee_pp_create'),
    path('employee_pp/edit/', views.employee_pp_edit, name='employee_pp_edit'),
    path('employee_pp/update/', views.employee_pp_update, name='employee_pp_update'),
    path('employee_pp/delete/', views.employee_pp_delete, name='employee_pp_delete'),
    path('get_employee_details_by_code/', views.get_employee_details_by_code, name='get_employee_details_by_code'),

    path('duty_roster/', views.duty_roster, name='duty_roster'),

    #enquiries
    path('employee_enquiries/', views.employee_enquiries, name='employee_enquiries'),
    path('attendance_enquiries/', views.attendance_enquiries, name='attendance_enquiries'),
    path('documents_enquiries/', payroll_views.documents_enquiries, name='documents_enquiries'),

    #labour
    path('labour_contract_condition/', views.LabourContractCondition.as_view(), name='labour_contract_condition'),
    path('labour-contract/delete/<int:labour_contract_id>/', views.LabourContractCondition.as_view(), name='delete_labour_contract'),

    #reports
    path('salary_register_single_line/', views.salary_register_single_line, name='salary_register_single_line'),
    path('salary_register_single_line_history/', views.salary_register_single_line_history, name='salary_register_single_line_history'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('salary_register_multi_line/', views.salary_register_multi_line, name='salary_register_multi_line'),
    path('salary_register_multi_line_history/', views.salary_register_multi_line_history, name='salary_register_multi_line_history'),
    path('control_statement/', views.control_statement, name='control_statement'),
    path('control_statement_history/', views.control_statement_history, name='control_statement_history'),
    path('pay_slip/', views.pay_slip, name='pay_slip'),
    path('pay_slip_history/', views.pay_slip_history, name='pay_slip_history'),
    path('get_employees_by_paycycle/', views.get_employees_by_paycycle, name='get_employees_by_paycycle'),
    path('get_employees_by_category/', views.get_employees_by_category, name='get_employees_by_category'),
    path('payment_wise_report/', views.payment_wise_report, name='payment_wise_report'),
    path('payment_wise_report_history/', views.payment_wise_report_history, name='payment_wise_report_history'),
    path('project_wise_job_summary/', views.project_wise_job_summary, name='project_wise_job_summary'),
    path('project_wise_report/', views.project_wise_report, name='project_wise_report'),
    path('project_wise_report_history/', views.project_wise_report_history, name='project_wise_report_history'),
    path('project_wise_job_summary_history/', views.project_wise_job_summary_history, name='project_wise_job_summary_history'),
    path('employee_details_report/', views.employee_details_report, name='employee_details_report'),
    path('employee_advance_report/', views.employee_advance_report, name='employee_advance_report'),
    path('employee_salary_detail/', views.employee_salary_detail, name='employee_salary_detail'),
    path('leave_tracker_report/', views.leave_tracker_report, name='leave_tracker_report'),
    path('document_tracker_report/', views.document_tracker_report, name='document_tracker_report'),
    # path('salary_register_multi_line_report/', views.salary_register_multi_line_report, name='salary_register_multi_line_report'),


    #procurement
    path('procurement/item_master/', procurement.item_master, name='item_master'),
    path('procurement/item_master_add/', procurement.item_master_add, name='item_master_add'),
    path('procurement/item_master_edit/', procurement.item_master_edit, name='item_master_edit'),
    path('procurement/item_master_delete/', procurement.item_master_delete, name='item_master_delete'),

    path('procurement/uom_master/', procurement.uom_master, name='uom_master'),
    path('procurement/uom_master_add/', procurement.uom_master_add, name='uom_master_add'),
    path('procurement/uom_master_edit/', procurement.uom_master_edit, name='uom_master_edit'),
    path('procurement/uom_master_delete/', procurement.uom_master_delete, name='uom_master_delete'),
    path('check_uom_exists/', procurement.check_uom_exists, name='check_uom_exists'),

    path('procurement/warehouse_master/', procurement.warehouse_master, name='warehouse_master'),
    path('procurement/warehouse_master_add/', procurement.warehouse_master_add, name='warehouse_master_add'),
    path('procurement/warehouse_master_edit/', procurement.warehouse_master_edit, name='warehouse_master_edit'),
    path('procurement/warehouse_master_delete/', procurement.warehouse_master_delete, name='warehouse_master_delete'),

    path('procurement/purchase_order/', procurement.purchase_order, name='purchase_order'),
    path('procurement/purchase_order_add/', procurement.purchase_order_add, name='purchase_order_add'),
    path('procurement/purchase_order_edit/', procurement.purchase_order_edit, name='purchase_order_edit'),
    path('procurement/purchase_order_delete/', procurement.purchase_order_delete, name='purchase_order_delete'),
    path('procurement/get_pr_items/', procurement.get_pr_items, name='get_pr_items'),

    path('procurement/grn/', procurement.grn, name='grn'),
    path('procurement/grn_add/', procurement.grn_add, name='grn_add'),
    path('procurement/grn_delete/', procurement.grn_delete, name='grn_delete'),
    path('procurement/get_po_items/', procurement.get_po_items, name='get_po_items'),

    path('procurement/material_request/', procurement.material_request, name='material_request'),
    path('procurement/material_request_add/', procurement.material_request_add, name='material_request_add'),
    path('procurement/material_request_edit/', procurement.material_request_edit, name='material_request_edit'),
    path('procurement/material_request_delete/', procurement.material_request_delete, name='material_request_delete'),

    path('procurement/warehouse_opening_stock/', procurement.warehouse_opening_stock, name='warehouse_opening_stock'),
    path('procurement/warehouse_opening_stock_add/', procurement.warehouse_opening_stock_add, name='warehouse_opening_stock_add'),
    path('procurement/warehouse_opening_stock_edit/', procurement.warehouse_opening_stock_edit, name='warehouse_opening_stock_edit'),
    path('procurement/warehouse_opening_stock_delete/', procurement.warehouse_opening_stock_delete, name='warehouse_opening_stock_delete'),
    path('procurement/get_item_details/', procurement.get_item_details, name='get_item_details'),

    path('procurement/material_issue/', procurement.material_issue, name='material_issue'),
    path('procurement/material_issue_add/', procurement.material_issue_add, name='material_issue_add'),
    path('procurement/material_issue_edit/', procurement.material_issue_edit, name='material_issue_edit'),
    path('procurement/material_issue_delete/', procurement.material_issue_delete, name='material_issue_delete'),
    path('procurement/get_mr_items/', procurement.get_mr_items, name='get_mr_items'),
    path('procurement/get_warehouse_stock/', procurement.get_warehouse_stock, name='get_warehouse_stock'),

    # Notification Master URLs
    path('notification/list/', views.notification_list, name='notification_list'),
    path('notification/create/', views.notification_create, name='notification_create'),
    path('notification/edit/', views.notification_edit, name='notification_edit'),
    path('notification/update/', views.notification_update, name='notification_update'),
    path('notification/delete/<int:notification_id>/', views.notification_delete, name='notification_delete'),

    # Offboarding URLs
    path('offboarding/', views.offboarding_list, name='offboarding_list'),
    path('offboarding/create/', views.offboarding_create, name='offboarding_create'),
    path('offboarding/edit/', views.offboarding_edit, name='offboarding_edit'),
    path('offboarding/delete/', views.offboarding_delete, name='offboarding_delete'),
    path('get_employee_offboarding_details/', views.get_employee_offboarding_details, name='get_employee_offboarding_details'),

    # Exit Process URLs
    path('exit_process/', views.exit_process_list, name='exit_process_list'),
    path('create_exit_process/', views.create_exit_process, name='create_exit_process'),
    path('update_exit_process/', views.update_exit_process, name='update_exit_process'),
    path('delete_exit_process/<int:exit_process_id>/', views.delete_exit_process, name='delete_exit_process'),
    path('get_exit_process_details_by_offboarding/', views.get_exit_process_details_by_offboarding, name='get_exit_process_details_by_offboarding'),

    # Cancellation Category Management URLs
    path('get_cancellation_categories/', views.get_cancellation_categories, name='get_cancellation_categories'),
    # Cancellation Sub-Category Management URLs
    path('get_sub_cancellation_categories/', views.get_sub_cancellation_categories, name='get_sub_cancellation_categories'),
    path('create_cancellation_sub_category/', views.create_cancellation_sub_category, name='create_cancellation_sub_category'),
    path('update_cancellation_sub_category/', views.update_cancellation_sub_category, name='update_cancellation_sub_category'),
    path('delete_cancellation_sub_category/', views.delete_cancellation_sub_category, name='delete_cancellation_sub_category'),
    path('get_cancellation_types_by_category/', views.get_cancellation_types_by_category, name='get_cancellation_types_by_category'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)