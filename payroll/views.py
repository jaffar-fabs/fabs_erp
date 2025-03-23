from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import uuid
from datetime import datetime, timedelta  # Import timedelta
import os
from django.conf import settings
from django.template import loader
from django.http import HttpResponse
import pandas as pd
from zipfile import BadZipFile
from security.models import UserRoleMapping, RoleMaster
from django.views import View
from .models import CodeMaster
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count
import pdb

PAGINATION_SIZE = 6

# Single import statement for models
from .models import (
    PaycycleMaster,
    projectMatster,
    HolidayMaster,
    CodeMaster,
    SeedModel,
    Menu,
    RoleMenu,
    UserMaster,
    CompanyMaster,
    GradeMaster, 
    Employee,
    WorkerAttendanceRegister
)

# Initialize COMP_CODE globally
COMP_CODE = None

def set_comp_code(request):
    global COMP_CODE
    COMP_CODE = request.session.get("comp_code")

def employee_master(request):
    set_comp_code(request)
    # Fetch all employee data for display
    employee_data = Employee.objects.filter(comp_code=COMP_CODE)
    return render(request, 'pages/payroll/employee_master/employee_master.html', {'employees': employee_data})

def save_employee(request, employee_id=None):
    set_comp_code(request)
    if request.method == "POST":
        if employee_id:
            employee = get_object_or_404(Employee, employee_id=employee_id)
            employee.modified_by = 1  # Replace with actual user ID if available
            employee.modified_on = now()
        else:
            employee = Employee()
            employee.created_by = 1  # Replace with actual user ID if available
            employee.created_on = now()

        # Assign values from request
        employee.comp_code = COMP_CODE
        employee.emp_code = request.POST.get("emp_code")
        employee.emp_name = request.POST.get("emp_name_passport")
        employee.surname = request.POST.get("surname")
        employee.dob = request.POST.get("dob") or None
        employee.emp_sex = request.POST.get("emp_sex")
        employee.emp_status = request.POST.get("emp_status")
        employee.father_name = request.POST.get("father_name")
        employee.mother_name = request.POST.get("mother_name")
        employee.nationality = request.POST.get("nationality")
        employee.religion = request.POST.get("religion")
        employee.qualification = request.POST.get("qualification")
        employee.emp_marital_status = request.POST.get("emp_marital_status")
        employee.spouse_name = request.POST.get("spouse_name")
        employee.height = request.POST.get("height") or None
        employee.weight = request.POST.get("weight") or None
        employee.family_status = request.POST.get("family_status") or None
        employee.res_country_code = request.POST.get("res_country_code")
        employee.res_phone_no = request.POST.get("res_phone_no")
        employee.res_addr_line1 = request.POST.get("res_addr_line1")
        employee.res_addr_line2 = request.POST.get("res_addr_line2")
        employee.res_city = request.POST.get("res_city")
        employee.res_state = request.POST.get("res_state")
        employee.local_city = request.POST.get("local_city")
        employee.local_state = request.POST.get("local_state")
        employee.local_country_code = request.POST.get("local_country_code")
        employee.local_phone_no = request.POST.get("local_phone_no")
        employee.local_addr_line1 = request.POST.get("local_addr_line1")
        employee.local_addr_line2 = request.POST.get("local_addr_line2")
        employee.labour_id = request.POST.get("labour_id")
        employee.process_cycle = request.POST.get("process_cycle")
        employee.basic_pay = request.POST.get("basic_pay") or None
        employee.allowance = request.POST.get("allowance") or None
        employee.grade_code = request.POST.get("grade_code")
        employee.designation = request.POST.get("designation")
        employee.department = request.POST.get("department")
        employee.date_of_join = request.POST.get("date_of_join") or None
        employee.date_of_rejoin = request.POST.get("date_of_rejoin") or None
        employee.depend_count = request.POST.get("depend_count") or None
        employee.child_count = request.POST.get("child_count") or None
        employee.employee_bank = request.POST.get("employee_bank")
        employee.bank_branch = request.POST.get("bank_branch")
        employee.account_no = request.POST.get("account_no")
        employee.bank_loan = request.POST.get("bank_loan") or None

        # File fields
        employee.passport_document = request.FILES.get("passport_document") or employee.passport_document
        employee.visa_document = request.FILES.get("visa_document") or employee.visa_document
        employee.emirate_document = request.FILES.get("emirate_document") or employee.emirate_document
        employee.work_permit_document = request.FILES.get("work_permit_document") or employee.work_permit_document
        employee.profile_picture = request.FILES.get("profile_picture") or employee.profile_picture
        employee.full_final_settlement_copy_id = request.POST.get("full_and_final_settlement_copy_id")
        employee.full_final_settlement_copy_file = request.FILES.get("full_and_final_settlement_copy_file") or employee.full_final_settlement_copy_file

        # Additional document fields
        employee.manpower_request_file = request.FILES.get("manpower_request_file") or employee.manpower_request_file
        employee.interview_assessment_file = request.FILES.get("interview_assessment_file") or employee.interview_assessment_file
        employee.passport_copy_file = request.FILES.get("passport_copy_file") or employee.passport_copy_file
        employee.photo_file = request.FILES.get("photo_file") or employee.photo_file
        employee.offer_letter_file = request.FILES.get("offer_letter_file") or employee.offer_letter_file
        employee.nominee_form_file = request.FILES.get("nominee_form_file") or employee.nominee_form_file
        employee.change_status_file = request.FILES.get("change_status_file") or employee.change_status_file
        employee.visa_copy_file = request.FILES.get("visa_copy_file") or employee.visa_copy_file
        employee.emirates_id_file = request.FILES.get("emirates_id_file") or employee.emirates_id_file
        employee.labor_contract_file = request.FILES.get("labor_contract_file") or employee.labor_contract_file
        employee.job_offer_file = request.FILES.get("job_offer_file") or employee.job_offer_file
        employee.salary_certificate_file = request.FILES.get("salary_certificate_file") or employee.salary_certificate_file
        employee.salary_transfer_letter_file = request.FILES.get("salary_transfer_letter_file") or employee.salary_transfer_letter_file
        employee.increment_letter_file = request.FILES.get("increment_letter_file") or employee.increment_letter_file
        employee.warning_letter_file = request.FILES.get("warning_letter_file") or employee.warning_letter_file
        employee.experience_letter_file = request.FILES.get("experience_letter_file") or employee.experience_letter_file
        employee.resignation_letter_file = request.FILES.get("resignation_letter_file") or employee.resignation_letter_file
        employee.termination_letter_file = request.FILES.get("termination_letter_file") or employee.termination_letter_file
        employee.employee_confidential_form_file = request.FILES.get("employee_confidential_form_file") or employee.employee_confidential_form_file
        employee.leave_application_file = request.FILES.get("leave_application_file") or employee.leave_application_file

        # Additional details
        employee.passport_details = request.POST.get("passport_details")
        employee.issued_date = request.POST.get("issued_date") or None
        employee.expiry_date = request.POST.get("expiry_date") or None
        employee.visa_no = request.POST.get("visa_no")
        employee.emirates_no = request.POST.get("emirates_no")
        employee.visa_issued = request.POST.get("visa_issued") or None
        employee.visa_expiry = request.POST.get("visa_expiry") or None
        employee.emirate_issued = request.POST.get("emirate_issued") or None
        employee.emirate_expiry = request.POST.get("emirate_expiry") or None
        employee.uid_number = request.POST.get("uid_number")
        employee.mohra_number = request.POST.get("mohra_number")
        employee.work_permit_number = request.POST.get("work_permit_number")
        employee.work_permit_expiry = request.POST.get("work_permit_expiry") or None

        employee.manpower_request_id = request.POST.get("manpower_request_id")
        employee.interview_assessment_id = request.POST.get("interview_assessment_id")
        employee.passport_copy_id = request.POST.get("passport_copy_id")
        employee.photo_id = request.POST.get("photo_id")
        employee.offer_letter_id = request.POST.get("offer_letter_id")
        employee.nominee_form_id = request.POST.get("nominee_form_id")
        employee.change_status_id = request.POST.get("change_status_id")
        employee.visa_copy_id = request.POST.get("visa_copy_id")
        employee.emirates_id_id = request.POST.get("emirates_id_id")
        employee.labor_contract_id = request.POST.get("labor_contract_id")
        employee.job_offer_id = request.POST.get("job_offer_id")
        employee.salary_certificate_id = request.POST.get("salary_certificate_id")
        employee.salary_transfer_letter_id = request.POST.get("salary_transfer_letter_id")
        employee.increment_letter_id = request.POST.get("increment_letter_id")
        employee.warning_letter_id = request.POST.get("warning_letter_id")
        employee.experience_letter_id = request.POST.get("experience_letter_id")
        employee.resignation_letter_id = request.POST.get("resignation_letter_id")
        employee.termination_letter_id = request.POST.get("termination_letter_id")
        employee.employee_confidential_form_id = request.POST.get("employee_confidential_form_id")
        employee.leave_application_id = request.POST.get("leave_application_id")

        employee.labor_contract_issued_date = request.POST.get("labor_contract_issued_date") or None
        employee.labor_contract_expiry_date = request.POST.get("labor_contract_expiry_date") or None
        employee.emirates_id_issued_date = request.POST.get("emirates_id_issued_date") or None
        employee.emirates_id_expiry_date = request.POST.get("emirates_id_expiry_date") or None
        employee.visa_issued_date = request.POST.get("visa_copy_issued_date") or None
        employee.visa_expiry_date = request.POST.get("visa_copy_expiry_date") or None
        employee.passport_issued_date = request.POST.get("passport_copy_issued_date") or None
        employee.passport_expiry_date = request.POST.get("passport_copy_expiry_date") or None

        # Dependent Details
        employee.father_visa_copy_id = request.POST.get("father_visa_copy_id")
        employee.father_visa_copy_issued_date = request.POST.get("father_visa_copy_issued_date") or None
        employee.father_visa_copy_expiry_date = request.POST.get("father_visa_copy_expiry_date") or None
        employee.father_visa_copy_file = request.FILES.get("father_visa_copy_file") or employee.father_visa_copy_file

        employee.father_emirates_id_id = request.POST.get("father_emirates_id_id")
        employee.father_emirates_id_issued_date = request.POST.get("father_emirates_id_issued_date") or None
        employee.father_emirates_id_expiry_date = request.POST.get("father_emirates_id_expiry_date") or None
        employee.father_emirates_id_file = request.FILES.get("father_emirates_id_file") or employee.father_emirates_id_file

        employee.father_passport_id = request.POST.get("father_passport_id")
        employee.father_passport_issued_date = request.POST.get("father_passport_issued_date") or None
        employee.father_passport_expiry_date = request.POST.get("father_passport_expiry_date") or None
        employee.father_passport_file = request.FILES.get("father_passport_file") or employee.father_passport_file

        employee.mother_visa_copy_id = request.POST.get("mother_visa_copy_id")
        employee.mother_visa_copy_issued_date = request.POST.get("mother_visa_copy_issued_date") or None
        employee.mother_visa_copy_expiry_date = request.POST.get("mother_visa_copy_expiry_date") or None
        employee.mother_visa_copy_file = request.FILES.get("mother_visa_copy_file") or employee.mother_visa_copy_file

        employee.mother_emirates_id_id = request.POST.get("mother_emirates_id_id")
        employee.mother_emirates_id_issued_date = request.POST.get("mother_emirates_id_issued_date") or None
        employee.mother_emirates_id_expiry_date = request.POST.get("mother_emirates_id_expiry_date") or None
        employee.mother_emirates_id_file = request.FILES.get("mother_emirates_id_file") or employee.mother_emirates_id_file

        employee.mother_passport_id = request.POST.get("mother_passport_id")
        employee.mother_passport_issued_date = request.POST.get("mother_passport_issued_date") or None
        employee.mother_passport_expiry_date = request.POST.get("mother_passport_expiry_date") or None
        employee.mother_passport_file = request.FILES.get("mother_passport_file") or employee.mother_passport_file

        employee.spouse_visa_copy_id = request.POST.get("spouse_visa_copy_id")
        employee.spouse_visa_copy_issued_date = request.POST.get("spouse_visa_copy_issued_date") or None
        employee.spouse_visa_copy_expiry_date = request.POST.get("spouse_visa_copy_expiry_date") or None
        employee.spouse_visa_copy_file = request.FILES.get("spouse_visa_copy_file") or employee.spouse_visa_copy_file

        employee.spouse_emirates_id_id = request.POST.get("spouse_emirates_id_id")
        employee.spouse_emirates_id_issued_date = request.POST.get("spouse_emirates_id_issued_date") or None
        employee.spouse_emirates_id_expiry_date = request.POST.get("spouse_emirates_id_expiry_date") or None
        employee.spouse_emirates_id_file = request.FILES.get("spouse_emirates_id_file") or employee.spouse_emirates_id_file

        employee.spouse_passport_id = request.POST.get("spouse_passport_id")
        employee.spouse_passport_issued_date = request.POST.get("spouse_passport_issued_date") or None
        employee.spouse_passport_expiry_date = request.POST.get("spouse_passport_expiry_date") or None
        employee.spouse_passport_file = request.FILES.get("spouse_passport_file") or employee.spouse_passport_file

        employee.child1_visa_copy_id = request.POST.get("child1_visa_copy_id")
        employee.child1_visa_copy_issued_date = request.POST.get("child1_visa_copy_issued_date") or None
        employee.child1_visa_copy_expiry_date = request.POST.get("child1_visa_copy_expiry_date") or None
        employee.child1_visa_copy_file = request.FILES.get("child1_visa_copy_file") or employee.child1_visa_copy_file

        employee.child1_emirates_id_id = request.POST.get("child1_emirates_id_id")
        employee.child1_emirates_id_issued_date = request.POST.get("child1_emirates_id_issued_date") or None
        employee.child1_emirates_id_expiry_date = request.POST.get("child1_emirates_id_expiry_date") or None
        employee.child1_emirates_id_file = request.FILES.get("child1_emirates_id_file") or employee.child1_emirates_id_file

        employee.child1_passport_id = request.POST.get("child1_passport_id")
        employee.child1_passport_issued_date = request.POST.get("child1_passport_issued_date") or None
        employee.child1_passport_expiry_date = request.POST.get("child1_passport_expiry_date") or None
        employee.child1_passport_file = request.FILES.get("child1_passport_file") or employee.child1_passport_file

        employee.child1_birth_certificate_file = request.FILES.get("child1_birth_certificate_file") or employee.child1_birth_certificate_file

        employee.child2_visa_copy_id = request.POST.get("child2_visa_copy_id")
        employee.child2_visa_copy_issued_date = request.POST.get("child2_visa_copy_issued_date") or None
        employee.child2_visa_copy_expiry_date = request.POST.get("child2_visa_copy_expiry_date") or None
        employee.child2_visa_copy_file = request.FILES.get("child2_visa_copy_file") or employee.child2_visa_copy_file

        employee.child2_emirates_id_id = request.POST.get("child2_emirates_id_id")
        employee.child2_emirates_id_issued_date = request.POST.get("child2_emirates_id_issued_date") or None
        employee.child2_emirates_id_expiry_date = request.POST.get("child2_emirates_id_expiry_date") or None
        employee.child2_emirates_id_file = request.FILES.get("child2_emirates_id_file") or employee.child2_emirates_id_file

        employee.child2_passport_id = request.POST.get("child2_passport_id")
        employee.child2_passport_issued_date = request.POST.get("child2_passport_issued_date") or None
        employee.child2_passport_expiry_date = request.POST.get("child2_passport_expiry_date") or None
        employee.child2_passport_file = request.FILES.get("child2_passport_file") or employee.child2_passport_file

        employee.child2_birth_certificate_file = request.FILES.get("child2_birth_certificate_file") or employee.child2_birth_certificate_file

        employee.child3_visa_copy_id = request.POST.get("child3_visa_copy_id")
        employee.child3_visa_copy_issued_date = request.POST.get("child3_visa_copy_issued_date") or None
        employee.child3_visa_copy_expiry_date = request.POST.get("child3_visa_copy_expiry_date") or None
        employee.child3_visa_copy_file = request.FILES.get("child3_visa_copy_file") or employee.child3_visa_copy_file

        employee.child3_emirates_id_id = request.POST.get("child3_emirates_id_id")
        employee.child3_emirates_id_issued_date = request.POST.get("child3_emirates_id_issued_date") or None
        employee.child3_emirates_id_expiry_date = request.POST.get("child3_emirates_id_expiry_date") or None
        employee.child3_emirates_id_file = request.FILES.get("child3_emirates_id_file") or employee.child3_emirates_id_file

        employee.child3_passport_id = request.POST.get("child3_passport_id")
        employee.child3_passport_issued_date = request.POST.get("child3_passport_issued_date") or None
        employee.child3_passport_expiry_date = request.POST.get("child3_passport_expiry_date") or None
        employee.child3_passport_file = request.FILES.get("child3_passport_file") or employee.child3_passport_file

        employee.child3_birth_certificate_file = request.FILES.get("child3_birth_certificate_file") or employee.child3_birth_certificate_file

        # Save employee
        employee.save()

        # Create folder for new employee
        if not employee_id:
            employee_folder_path = os.path.join(settings.MEDIA_ROOT, 'employee_documents', employee.emp_code)
            os.makedirs(employee_folder_path, exist_ok=True)

        return redirect('/employee')

    employee_data = Employee.objects.filter(comp_code=COMP_CODE)
    return render(request, 'pages/payroll/employee_master/employee_master.html', {'employees': employee_data})

def deactivate_employee(request, employee_id):
    set_comp_code(request)
    if request.method == 'POST':
        # Get the Employee object
        employee = get_object_or_404(Employee, employee_id=employee_id)
        # Update is_active to False
        employee.emp_status = 'inactive'
        employee.save()
        messages.success(request, 'Employee deactivated successfully!')
    return redirect('/employee')  # Redirect to the employee list page

def index(request):
    set_comp_code(request)
    
    # Count records for each model
    employee_count = Employee.objects.filter(comp_code=COMP_CODE).count()
    project_count = projectMatster.objects.filter(comp_code=COMP_CODE).count()
    holiday_count = HolidayMaster.objects.filter(comp_code=COMP_CODE).count()
    seed_count = SeedModel.objects.filter(comp_code=COMP_CODE).count()
    paycycle_count = PaycycleMaster.objects.filter(comp_code=COMP_CODE).count()
    company_count = CompanyMaster.objects.filter(company_code=COMP_CODE).count()
    grade_count = GradeMaster.objects.filter(comp_code=COMP_CODE).count()
    user_count = UserMaster.objects.filter(comp_code=COMP_CODE).count()
    
    context = {
        'employee_count': employee_count,
        'project_count': project_count,
        'holiday_count': holiday_count,
        'seed_count': seed_count,
        'paycycle_count': paycycle_count,
        'company_count': company_count,
        'grade_count': grade_count,
        'user_count': user_count,
    }
    
    return render(request, 'pages/dashboard/index.html', context)

def my_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = UserMaster.objects.get(user_id=username, is_active=True)

            if password == user.password:
                request.session["username"] = user.user_id
                request.session["comp_code"] = user.comp_code  # Set comp_code in session

                # Fetch role ID from UserRoleMapping
                user_role_mapping = UserRoleMapping.objects.get(userid=user.user_master_id, is_active=True)
                role_id = user_role_mapping.roleid

                # Fetch role name from RoleMaster
                role = RoleMaster.objects.get(id=role_id)
                request.session["role"] = role.role_name
                request.session["role_id"] = role_id

                set_comp_code(request)
                
                # messages.success(request, "Login successful!")
                return redirect("/index")
            else:
                messages.error(request, "Invalid username or password.")
        except UserMaster.DoesNotExist:
            messages.error(request, "Invalid username or password.")
        except UserRoleMapping.DoesNotExist:
            messages.error(request, "User role mapping not found.")
        except RoleMaster.DoesNotExist:
            messages.error(request, "Role not found.")

    return render(request, "auth/login.html")

def dashboard_view(request):
    set_comp_code(request)
    try:
        role_id = request.session.get("role_id")
        menu_ids = RoleMenu.objects.filter(role_id=role_id, view=True).values_list('menu_id', flat=True)
        parent_menu_data = list(Menu.objects.filter(menu_id__in=menu_ids, parent_menu_id='No Parent', comp_code=COMP_CODE).order_by('display_order').values('menu_id', 'screen_name'))
        child_menu_data = list(Menu.objects.filter(menu_id__in=menu_ids, comp_code=COMP_CODE).exclude(parent_menu_id='No Parent').order_by('display_order').values('menu_id', 'screen_name', 'url', 'parent_menu_id'))
        response_data = {'status': 'success', 'parent_menu_data': parent_menu_data, 'child_menu_data': child_menu_data}
    except Exception as e:
        response_data = {'status': 'error', 'msg': str(e)}

    return JsonResponse(response_data)

def logout(request):
    request.session.flush()  # Clears all session data
    # messages.success(request, "You have been logged out successfully.")
    return redirect("/")  # Redirect to login page

#-------------------------------

#Seed Master View

def create_seed(request):
    set_comp_code(request)
    if request.method == "POST":
        seed_code = request.POST.get("seed_code")
        seed_group = request.POST.get("seed_group")
        seed_type = request.POST.get("seed_type")
        seed_prefix = request.POST.get("seed_prefix")
        seed_length = request.POST.get("seed_length")
        seed_start_num = request.POST.get("seed_start_num")
        seed_next_num = request.POST.get("seed_next_num")
        seed_timeline_from = request.POST.get("seed_timeline_from")
        seed_timeline_to = request.POST.get("seed_timeline_to")
        seed_inc_by = request.POST.get("seed_inc_by")
        is_active = request.POST.get("status") == "active"
        
        created_by = 1  # Example user ID
        modified_by = 1  # Example user ID

        SeedModel.objects.create(
            comp_code=COMP_CODE,
            seed_code=seed_code,
            seed_group=seed_group,
            seed_type=seed_type,
            seed_prefix=seed_prefix,
            seed_length=seed_length,
            seed_start_num=seed_start_num,
            seed_next_num=seed_next_num,
            seed_timeline_from=seed_timeline_from,
            seed_timeline_to=seed_timeline_to,
            seed_inc_by=seed_inc_by,
            is_active=is_active,
            created_by=created_by,
            modified_by=modified_by
        )
        return redirect('create_seed')

    seed_data = SeedModel.objects.filter(comp_code=COMP_CODE)
    return render(request, 'pages/payroll/seed_master/seedmaster.html', {'seed_data': seed_data})

def update_seed_status(request, seed_id):
    set_comp_code(request)
    if request.method == 'POST':
        seed = get_object_or_404(SeedModel, seed_id=seed_id, comp_code=COMP_CODE)
        seed.is_active = False
        seed.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def edit_seed(request, seed_id):
    set_comp_code(request)
    seed = get_object_or_404(SeedModel, seed_id=seed_id, comp_code=COMP_CODE)

    if request.method == 'POST':
        # Update the seed with the submitted data
        seed.seed_code = request.POST.get('seed_code')
        seed.seed_group = request.POST.get('seed_group')
        seed.seed_type = request.POST.get('seed_type')
        seed.seed_prefix = request.POST.get('seed_prefix')
        seed.seed_length = request.POST.get('seed_length')
        seed.seed_start_num = request.POST.get('seed_start_num')
        seed.seed_next_num = request.POST.get('seed_next_num')
        seed.seed_inc_by = request.POST.get('seed_inc_by')
        seed.seed_timeline_from = request.POST.get('seed_timeline_from')
        seed.seed_timeline_to = request.POST.get('seed_timeline_to')
        
        # Update the status based on the form input
        seed.is_active = request.POST.get('status') == 'active'

        # Set the modified_by field
        seed.modified_by = 1  # Example: Use the logged-in user ID if available

        # Save changes to the database
        seed.save()

        # Redirect after successful update
        return redirect('create_seed')
    else:
        # Render the edit modal with existing seed data
        return render(request, 'pages/modal/payroll/seed-modal.html', {'seed': seed})


def get_seed(request, seed_id):
    set_comp_code(request)  # Ensures the company code is set in the session or context
    # Safely fetch the seed object; raises 404 if not found
    seed = get_object_or_404(SeedModel, seed_id=seed_id, comp_code=COMP_CODE)

    # Prepare the response data
    data = {
        'seed_code': seed.seed_code,
        'seed_group': seed.seed_group,
        'seed_type': seed.seed_type,
        'seed_prefix': seed.seed_prefix,
        'seed_length': seed.seed_length,
        'seed_start_num': seed.seed_start_num,
        'seed_next_num': seed.seed_next_num,
        'seed_inc_by': seed.seed_inc_by,
        'seed_timeline_from': seed.seed_timeline_from.strftime('%Y-%m-%d'),
        'seed_timeline_to': seed.seed_timeline_to.strftime('%Y-%m-%d'),
        'is_active': seed.is_active,
    }

    # Return the response as JSON
    return JsonResponse(data)


#--------------------------------------------------


class Paycycle(View):
    template_name = "pages/payroll/paycycle_master/paycycle-list.html"

    def get(self, request):
        set_comp_code(request)
        paycycle_list = PaycycleMaster.objects.filter(comp_code=COMP_CODE).order_by('-created_on')
        return render(request, self.template_name, {"paycycle_list": paycycle_list})

    def post(self, request):
        set_comp_code(request)
        process_cycle_id = request.POST.get('process_cycle_id')
        process_description = request.POST.get('process_description')
        process_cycle = request.POST.get('process_cycle')
        pay_process_month = request.POST.get('pay_process_month')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        process_date = request.POST.get('process_date')
        attendance_uom = request.POST.get('attendance_uom')
        default_project = request.POST.get('default_project')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        hours_per_day = request.POST.get('hours_per_day')
        days_per_month = request.POST.get('days_per_month')
        travel_time = request.POST.get('travel_time') or None
        lunch_break = request.POST.get('lunch_break') or None
        ot_eligible = request.POST.get('ot_eligible')
        ot2_eligible = request.POST.get('ot2_eligible')
        max_mn_hrs = request.POST.get('max_mn_hrs')
        max_an_hrs = request.POST.get('max_an_hrs')
        max_ot1_hrs = request.POST.get('max_ot1_hrs')
        ot1_amt = request.POST.get('ot1_amt')
        max_ot2_hrs = request.POST.get('max_ot2_hrs')
        ot2_amt = request.POST.get('ot2_amt')
        process_comp_flag = request.POST.get('process_comp_flag')
        is_active = "Y" if "is_active" in request.POST else "N"
        
        if process_cycle_id:
            paycycle = get_object_or_404(PaycycleMaster, process_cycle_id=process_cycle_id, comp_code=COMP_CODE)
            paycycle.process_description = process_description
            paycycle.process_cycle = process_cycle
            paycycle.pay_process_month = pay_process_month
            paycycle.date_from = date_from
            paycycle.date_to = date_to
            paycycle.process_date = process_date
            paycycle.attendance_uom = attendance_uom
            paycycle.default_project = default_project
            paycycle.start_time = start_time
            paycycle.end_time = end_time
            paycycle.hours_per_day = hours_per_day
            paycycle.days_per_month = days_per_month
            paycycle.travel_time = travel_time
            paycycle.lunch_break = lunch_break
            paycycle.ot_eligible = ot_eligible
            paycycle.ot2_eligible = ot2_eligible
            paycycle.max_mn_hrs = max_mn_hrs
            paycycle.max_an_hrs = max_an_hrs
            paycycle.max_ot1_hrs = max_ot1_hrs
            paycycle.ot1_amt = ot1_amt
            paycycle.max_ot2_hrs = max_ot2_hrs
            paycycle.ot2_amt = ot2_amt
            paycycle.process_comp_flag = process_comp_flag
            paycycle.is_active = is_active
            paycycle.modified_by = 1
            paycycle.modified_on = now()
            paycycle.save()
        else:
            PaycycleMaster.objects.create(
                comp_code=COMP_CODE,
                process_description=process_description,
                process_cycle_id=self.get_next_process_cycle_id(),
                process_cycle=process_cycle,
                pay_process_month=pay_process_month,
                date_from=date_from,
                date_to=date_to,
                attendance_uom=attendance_uom,
                process_date=process_date,
                default_project=default_project,
                start_time=start_time,
                end_time=end_time,
                hours_per_day=hours_per_day,
                days_per_month=days_per_month,
                travel_time=travel_time,
                lunch_break=lunch_break,
                ot_eligible=ot_eligible,
                ot2_eligible=ot2_eligible,
                max_mn_hrs=max_mn_hrs,
                max_an_hrs=max_an_hrs,
                max_ot1_hrs=max_ot1_hrs,
                ot1_amt=ot1_amt,
                max_ot2_hrs=max_ot2_hrs,
                ot2_amt=ot2_amt,
                process_comp_flag=process_comp_flag,
                is_active=is_active,
                created_by=1,
                created_on=now(),
            )

        return redirect("payroll_paycycle_master")

    def delete(self, request, process_cycle_id):
        set_comp_code(request)
        paycycle = get_object_or_404(PaycycleMaster, process_cycle_id=process_cycle_id, comp_code=COMP_CODE)
        paycycle.is_active = "N"
        paycycle.save()
        return JsonResponse({"status": "success", "message": "Paycycle deactivated successfully."})


    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def get_next_process_cycle_id(request,self):
        set_comp_code(request)
        auto_paycycle_id = PaycycleMaster.objects.filter(comp_code=COMP_CODE).order_by('-process_cycle_id').first()
        return auto_paycycle_id.process_cycle_id + 1 if auto_paycycle_id else 1
    
def project(request):
    set_comp_code(request)
    template_name = 'pages/payroll/project_master/projects.html'
    def col2num(self, col):
        import string
        num = 0
        for c in col:
            if c in string.ascii_letters:
                num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        return num-1
    project_id = request.GET.get("project_id")
    print(project_id, 'project_id')
    if request.method == "GET":
        if project_id:  # If `project_id` exists, return a JSON response with project data
            try:
                project = projectMatster.objects.get(project_id=project_id, comp_code=COMP_CODE)
                return JsonResponse({
                    "project_id": project.project_id,
                    "prj_code": project.prj_code,
                    "prj_name": project.prj_name,
                    "project_description": project.project_description,
                    "project_type": project.project_type,
                    "project_value": project.project_value,
                    "timeline_from": project.timeline_from,
                    "timeline_to": project.timeline_to,
                    "prj_city": project.prj_city,
                    "consultant": project.consultant,
                    "main_contractor": project.main_contractor,
                    "sub_contractor": project.sub_contractor,
                    "is_active": project.is_active,
                    "comp_code": project.comp_code,
                })
            except projectMatster.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)
        
        else:  # If `project_id` doesn't exist, render the page with paginated results
            # Handle keyword and pagination logic
            keyword = request.GET.get('keyword', '').strip()
            page_number = request.GET.get('page', 1)
            get_url = request.get_full_path()

            print(keyword, 'keyword')
            print(page_number, 'page_number')

            # Adjust URL for pagination
            if '?keyword' in get_url:
                get_url = get_url.split('&page=')[0]
                current_url = f"{get_url}&"
            else:
                get_url = get_url.split('?')[0]
                current_url = f"{get_url}?"

            # Initialize the query
            query = projectMatster.objects.filter(comp_code=COMP_CODE)

            # Apply search filter if a keyword is provided
            if keyword:
                try:
                    query = query.filter(
                        Q(prj_code__icontains=keyword) |
                        Q(prj_name__icontains=keyword) |
                        Q(project_description__icontains=keyword) |
                        Q(prj_city__icontains=keyword)
                    )
                except Exception as e:
                    print(f"Error in keyword search: {e}")
                    return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

            # Apply pagination
            paginator = Paginator(query.order_by('project_id'), PAGINATION_SIZE)
            
            try:
                projects_page = paginator.get_page(page_number)
            except PageNotAnInteger:
                projects_page = paginator.page(1)
            except EmptyPage:
                projects_page = paginator.page(paginator.num_pages)

            # Prepare the paginated results
            projects_data = []
            for project in projects_page:
                projects_data.append({
                    "project_id": project.project_id,
                    "prj_code": project.prj_code,
                    "prj_name": project.prj_name,
                    "project_description": project.project_description,
                    "project_type": project.project_type,
                    "project_value": project.project_value,
                    "timeline_from": project.timeline_from,
                    "timeline_to": project.timeline_to,
                    "prj_city": project.prj_city,
                    "consultant": project.consultant,
                    "main_contractor": project.main_contractor,
                    "sub_contractor": project.sub_contractor,
                    "is_active": project.is_active,
                    "comp_code": project.comp_code,
                })

            # Prepare the context for the template
            context = {
                'projects': projects_page,
                'current_url': current_url,
                'keyword': keyword,
                'result_cnt': query.count()
            }

            print(context, 'context')

            # Render the template
            return render(request, template_name, context)
       
    if request.method == "POST":
        
            project_id = request.POST.get("project_id")
            if projectMatster.objects.filter(project_id=project_id, comp_code=COMP_CODE).exists():
                project = get_object_or_404(projectMatster, project_id=int(project_id), comp_code=COMP_CODE)

                project.prj_code = request.POST.get("project_code", project.prj_code)
                project.prj_name = request.POST.get("project_name", project.prj_name)
                project.project_description = request.POST.get("project_description", project.project_description)
                project.project_type = request.POST.get("project_type", project.project_type)
                project.project_value = request.POST.get("project_value", project.project_value)
                project.timeline_from = request.POST.get("timeline_from", project.timeline_from)
                project.timeline_to = request.POST.get("timeline_to", project.timeline_to)
                project.prj_city = request.POST.get("prj_city", project.prj_city)
                project.consultant = request.POST.get("consultant", project.consultant)
                project.main_contractor = request.POST.get("main_contractor", project.main_contractor)
                project.sub_contractor = request.POST.get("sub_contractor", project.sub_contractor)
                project.is_active = request.POST.get("is_active") == "Active"
                project.created_by=1
                project.comp_code = request.POST.get("comp_code", project.comp_code)

                project.save()
                return redirect("project")

            else:
                prj_code=request.POST.get("project_code")
                # if projectMatster.objects.filter(prj_code=prj_code).exists():
                #     return JsonResponse(
                #      {
                #          "error": "Project Code already exists"
                #          }
                #     )
                project = projectMatster(
                prj_code=request.POST.get("project_code"),
                prj_name=request.POST.get("project_name"),
                project_description=request.POST.get("project_description", "No description available"),
                project_type=request.POST.get("project_type", 0),
                project_value=request.POST.get("project_value", 0.00),
                timeline_from=request.POST.get("timeline_from", "Not specified"),
                timeline_to=request.POST.get("timeline_to", "Not specified"),
                prj_city=request.POST.get("prj_city", 0),
                created_by=1,
                consultant=request.POST.get("consultant", "Not Assigned"),
                main_contractor=request.POST.get("main_contractor", "Not Assigned"),
                sub_contractor=request.POST.get("sub_contractor", "Not Assigned"),
                is_active=request.POST.get("is_active") == "Active",
                comp_code=COMP_CODE,
                )
                project.save()
            return redirect("project")


    # # projects = projectMatster.objects.filter(is_active=True).order_by('-created_on')
    # projects = projectMatster.objects.filter(comp_code=COMP_CODE).order_by('-created_on')
    # project_count=projectMatster.objects.filter(comp_code=COMP_CODE)
    # print("COUNT ",project_count)
    return render(request, template_name, context=context)


def check_project_code(request):
    set_comp_code(request)
    if request.method == "POST":
        project_code = request.POST.get("project_code")

        if projectMatster.objects.filter(prj_code=project_code, comp_code=COMP_CODE).exists():
            return JsonResponse({"exists": True})  # Project code exists
        else:
            return JsonResponse({"exists": False})  # Project code is unique

    return JsonResponse({"error": "Invalid request"}, status=400)


def delete_project(request):
    set_comp_code(request)
    if request.method == "POST":
        project_id = request.POST.get("project_id")

        if project_id:
            project = get_object_or_404(projectMatster, project_id=project_id, comp_code=COMP_CODE)
            project.is_active = False  
            project.save()
    return redirect("project")

# Holiday Master -------------------------

# class HolidayMaster(View):


class CodeMasterList(View):

    template_name = "pages/payroll/code_master/code_master_list.html"

    def get(self, request): 
        base_type_suggestions = CodeMaster.objects.filter(comp_code="999").values("base_description", "base_value").distinct()
        # ...existing code...
        used_base_codes = [
            'SEX', 'PROCESS CYCLE', 'PROCESS COMPLETION FLAG', 'STATUS', 'MARITAL STATUS', 
            'DESIGNATION', 'DEPT', 'ATTENDANCE UOM', 'PROJECT TYPE', 'PROJECT CITY', 
            'NATIONALITY', 'HOLIDAY'
        ]
        base_type_comp_code = CodeMaster.objects.filter(comp_code="999", base_value__in=used_base_codes).values("base_value", "base_description").distinct()
        return render(request, self.template_name, { "base_type_suggestions": base_type_suggestions, "base_type_comp_code": base_type_comp_code })

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @csrf_exempt
    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            request_type = request.POST.get("request_type")
            if request_type == "check_base_value_exists":
                return self.check_base_value_exists(request)
            if request_type == "fetch_base_description":
                return self.fetch_base_description(request)
            elif request_type == "update_base_description":
                return self.update_base_description(request)
            elif request_type == "delete_base_value":
                return self.delete_base_value(request)
            return self.handle_ajax(request)
        return self.handle_form_submission(request)

    @csrf_exempt
    def check_base_value_exists(self, request):
        base_value = request.POST.get("base_value")
        base_type = request.POST.get("base_type")
        if CodeMaster.objects.filter(base_type=base_type, base_value=base_value, comp_code=COMP_CODE).exists():
            return JsonResponse({"exists": True})
        return JsonResponse({"exists": False})

    def update_base_description(self, request):
        base_code = request.POST.get("base_code")
        base_value = request.POST.get("base_value")
        base_description = request.POST.get("base_description")
        is_active = request.POST.get("is_active")

        if not all([base_code, base_value, base_description, is_active]):
            return JsonResponse({"success": False, "error": "Invalid input data"})

        try:
            code_master = CodeMaster.objects.filter(base_type=base_code, base_value=base_value, comp_code=COMP_CODE).first()
            if code_master:
                code_master.base_description = base_description
                code_master.is_active = is_active
                code_master.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "No matching record found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    @csrf_exempt
    def handle_ajax(self, request):
        base_code = request.POST.get("base_code")
        if base_code:
            base_values = CodeMaster.objects.filter(base_type=base_code, comp_code=COMP_CODE).values("base_value", "is_active")
            base_values_list = [{"base_value": value["base_value"], "is_active": value["is_active"]} for value in base_values]
            return JsonResponse({"success": True, "base_values": base_values_list})
        return JsonResponse({"success": False, "error": "Invalid base code"})

    def handle_form_submission(self, request):
        base_description = request.POST.get("base_description")
        base_value = request.POST.get("base_value")
        description = request.POST.get("description")
        is_active = "Y" if "is_active" in request.POST else "N"

        base_type_obj = CodeMaster.objects.filter(base_description=base_description, comp_code="999").values("base_value").first()
        base_type = base_type_obj["base_value"] if base_type_obj else None

        if base_type and base_value:
            existing_entry = CodeMaster.objects.filter(comp_code=COMP_CODE, base_type=base_type, base_value=base_value).exists()
            if not existing_entry:
                CodeMaster.objects.create(
                    comp_code=COMP_CODE,
                    base_type=base_type,
                    base_value=base_value,
                    base_description=description,
                    sequence_id=CodeMaster.objects.count() + 1,
                    instance_id="INSTANCE_1",
                    created_by=1,
                    is_active=is_active,
                )
        return redirect("code_master_list")

    @csrf_exempt
    def fetch_base_description(self, request):
        base_code = request.POST.get("base_code")
        base_value = request.POST.get("base_value")
        if base_code and base_value:
            base_description_obj = CodeMaster.objects.filter(base_type=base_code, base_value=base_value, comp_code=COMP_CODE).values("base_description", "is_active").first()
            if base_description_obj:
                is_active = base_description_obj["is_active"] == "Y"
                return JsonResponse({"success": True, "base_description": base_description_obj["base_description"], "is_active": is_active})
            return JsonResponse({"success": False, "error": "No matching record found"})
        else:
            return JsonResponse({"success": False, "error": "Invalid input data"})

    @csrf_exempt
    def delete_base_value(self, request):
        base_code = request.POST.get("base_code")
        base_value = request.POST.get("base_value")

        if not all([base_code, base_value]):
            return JsonResponse({"success": False, "error": "Invalid input data"})

        try:
            code_master = CodeMaster.objects.filter(base_type=base_code, base_value=base_value, comp_code=COMP_CODE).first()
            if code_master:
                code_master.is_active = "N"
                code_master.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "No matching record found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})



class Login(View):
    template_name = 'auth/login.html'
    
    def get(self, request):
        return render(self.request, self.template_name)

class UserMasterList(View):
    template_name = 'pages/payroll/user/user_master.html'

    def get(self, request):
        users = UserMaster.objects.filter(comp_code=COMP_CODE)
        print(users)
        return render(request, self.template_name, {'users': users})

from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views import View
from .models import UserMaster
from django.urls import reverse


class UserMasterCreate(View):
    def post(self, request):
        user_id = request.POST.get('user_id', '').strip()

        if not user_id:
            return JsonResponse({'status': 'error', 'field': 'user_id', 'message': 'User ID is required.'})

        if request.POST.get("check_availability") == "true":
            if UserMaster.objects.filter(user_id=user_id, comp_code=COMP_CODE).exists():
                return JsonResponse({'status': 'error', 'field': 'user_id', 'message': 'User ID already exists.'})
            return JsonResponse({'status': 'success', 'message': 'User ID is available.'})

        if UserMaster.objects.filter(user_id=user_id, comp_code=COMP_CODE).exists():
            return JsonResponse({'status': 'error', 'field': 'user_id', 'message': 'User ID already exists.'})

        try:
            user = UserMaster(
                comp_code=COMP_CODE,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                user_id=user_id,
                password=request.POST.get('password'),
                dob=request.POST.get('dob') or None, 
                email=request.POST.get('email'),
                gender=request.POST.get('gender'),
                is_active=request.POST.get('is_active') == 'on',
                instance_id=100000000,
                profile_picture=request.FILES.get('profile_picture'),
                created_by=request.POST.get('created_by'),
                modified_by=request.POST.get('modified_by'),
                emp_code=request.POST.get('emp_code'),
                user_paycycles=request.POST.get('user_paycycles')
            )

            user.full_clean()
            user.save()
            return JsonResponse({'status': 'success', 'redirect_url': reverse('user_list')})

        except Exception as e:
            return JsonResponse({'status': 'error', 'field': 'general', 'message': str(e)})

class UserMasterUpdate(View):
    def post(self, request, user_master_id):
        try:
            user = get_object_or_404(UserMaster, user_master_id=user_master_id, comp_code=COMP_CODE)
    
            user.comp_code = COMP_CODE
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.user_id = request.POST.get('user_id')
            user.password = request.POST.get('password')
            user.dob = request.POST.get('dob') or None  # Make DOB optional
            user.email = request.POST.get('email')
            user.gender = request.POST.get('gender')
            user.instance_id = request.POST.get('instance_id')
            user.profile_picture = request.FILES.get('profile_picture')
            user.modified_by = request.POST.get('modified_by')
            user.emp_code = request.POST.get('emp_code')
            user.user_paycycles = request.POST.get('user_paycycles')
            user.is_active = request.POST.get('is_active') == 'on'
            
            user.full_clean()
            user.save()
            
            return redirect('user_list')

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
class UserMasterDelete(View):
    def post(self, request, user_master_id):
        
        user = get_object_or_404(UserMaster, user_master_id=user_master_id, comp_code=COMP_CODE)
        
        user.is_active = False
        user.save()  
        
        return redirect('user_list')
    
        
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import GradeMaster
from django.utils.timezone import now

class GradeMasterList(View):
    template_name = "pages/payroll/grade_master/grade_master_list.html"

    def get(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            grade_code = request.GET.get('grade_code', None)
            data = {
                'exists': GradeMaster.objects.filter(grade_code=grade_code, comp_code=COMP_CODE).exists()
            }
            print(data)
            return JsonResponse(data)

        datas = GradeMaster.objects.filter(comp_code=COMP_CODE)
        return render(request, self.template_name, {'datas': datas})


    def post(self, request):
        # Check for delete request
        if "delete_grade_id" in request.POST:
            grade_id = request.POST.get("delete_grade_id")
            GradeMaster.objects.filter(grade_id=grade_id, comp_code=COMP_CODE).update(is_active="N")
            return redirect("grade_master")

        # Extract form data for edit operation
        grade_id = request.POST.get("grade_id")
        grade_code = request.POST.get("grade_code")
        grade_desc = request.POST.get("grade_desc")
        nationality = request.POST.get("nationality")
        attendance_days = request.POST.get("attendance_days") or 0
        leave_days = request.POST.get("leave_days") or 0
        passage_amount_adult = request.POST.get("passage_amount_adult") or 0.0
        passage_amount_child = request.POST.get("passage_amount_child") or 0.0

        # Convert Allowances
        allowances = {
            "allowance1": request.POST.get("allowance1") or None,
            "allowance2": request.POST.get("allowance2") or None,
            "allowance3": request.POST.get("allowance3") or None,
            "allowance4": request.POST.get("allowance4") or None,
            "allowance5": request.POST.get("allowance5") or None,
            "allowance6": request.POST.get("allowance6") or None,
            "allowance7": request.POST.get("allowance7") or None,
            "allowance8": request.POST.get("allowance8") or None,
        }
        is_active = "Y" if "is_active" in request.POST else "N"
        designation = request.POST.get("designation")

        if grade_id:
            grade = get_object_or_404(GradeMaster, grade_id=grade_id, comp_code=COMP_CODE)
            grade.grade_code = grade_code
            grade.grade_desc = grade_desc
            grade.nationality = nationality
            grade.attendance_days = int(attendance_days)
            grade.leave_days = int(leave_days)
            grade.passage_amount_adult = float(passage_amount_adult)
            grade.passage_amount_child = float(passage_amount_child)
            for key, value in allowances.items():
                setattr(grade, key, value)
            grade.is_active = is_active
            grade.designation = designation
            grade.modified_by = 1
            grade.modified_on = now()
            grade.save()
        else:
            set_comp_code(request)
            grade = GradeMaster.objects.create(
                comp_code=COMP_CODE,
                grade_code=grade_code,
                grade_desc=grade_desc,
                nationality=nationality,
                attendance_days=int(attendance_days),
                leave_days=int(leave_days),
                passage_amount_adult=float(passage_amount_adult),
                passage_amount_child=float(passage_amount_child),
                is_active=is_active,
                created_by=1,
                created_on=now(),
                instance_id='INSTANCE001',
                designation=designation,
            )
            for key, value in allowances.items():
                setattr(grade, key, value)
            grade.save()

        return redirect("grade_master")

# HOLIDAY ---------------------------------  HOLIDAY ----------------------------------------

def holidayList( request):
    set_comp_code(request)
    template_name="pages/payroll/holiday_master/holiday_list.html"
    holidays_list=HolidayMaster.objects.filter(comp_code=COMP_CODE).order_by('-created_on')
    holiday_type=CodeMaster.objects.filter(comp_code=COMP_CODE,base_type ='HOLIDAY')
    return render(request,template_name, {'holidays':holidays_list,'holidayTypes':holiday_type})
        

def holidayCreate(request):
    set_comp_code(request)
    if request.method == "POST":
        
            
        holiday = HolidayMaster(
            comp_code=COMP_CODE,
            holiday=request.POST.get("holiday"),
            holiday_type=request.POST.get("holiday_type"),
            holiday_date=request.POST.get("holiday_date"),
            holiday_day=request.POST.get("holiday_day"),
            holiday_description=request.POST.get("holiday_description"),
            is_active=request.POST.get("is_active") == "Active",
            created_by=1,
        )
        holiday.save()

        # Redirect after saving
        return redirect('holiday_master')

    # Redirect GET requests too
    return redirect('holiday_master')    

def holidayEdit(request):
    set_comp_code(request)
    if request.method == "GET":
        uniqe_id = request.GET.get("holiday_id")
    try:
            holiday = get_object_or_404(HolidayMaster, unique_id=int(uniqe_id), comp_code=COMP_CODE)
            # print(holiday.holiday_day,"DAY")
            return JsonResponse({
                "holiday_id":holiday.unique_id,
                "holiday": holiday.holiday,
                "holiday_day": holiday.holiday_day,
                "holiday_date": holiday.holiday_date,
                "holiday_description": holiday.holiday_description,
                "holiday_type": holiday.holiday_type,
                "is_active": holiday.is_active,
                "comp_code": holiday.comp_code,
            })
                    
    except Exception as e:
            print(f" Error project Edit: {str(e)}")  

    if request.method == "POST":
            holiday_id=request.POST.get("holiday_id")
            if HolidayMaster.objects.filter(unique_id=holiday_id, comp_code=COMP_CODE).exists():
                holiday = get_object_or_404(HolidayMaster, unique_id=int(holiday_id), comp_code=COMP_CODE)
                holiday.holiday = request.POST.get("holiday", holiday.holiday)
                holiday.holiday_date = request.POST.get("holiday_date", holiday.holiday_date)
                holiday.holiday_day = request.POST.get("holiday_day", holiday.holiday_day)
                holiday.holiday_type = request.POST.get("holiday_type", holiday.holiday_type)
                holiday.holiday_description = request.POST.get("holiday_description", holiday.holiday_description)
                holiday.created_by = 1
                holiday.comp_code = COMP_CODE
                holiday.is_active = request.POST.get("is_active") == "Active"
                holiday.save()
                return redirect("holiday_master")

def check_holiday(request):
    set_comp_code(request)
    if request.method == "POST":
        holiday = request.POST.get("holiday")
        holiday_date = request.POST.get("holiday_date")

        if HolidayMaster.objects.filter(holiday=holiday, holiday_date=holiday_date, comp_code=COMP_CODE).exists():
            return JsonResponse({"exists": True})  # Duplicate found
        else:
            return JsonResponse({"exists": False})  # Unique entry

    return JsonResponse({"error": "Invalid request"}, status=400)




class MenuMaster(View):
    template_name = "pages/security/menu_master/menu_list.html"

    def get(self, request, menu_id=None):
        if menu_id and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            menu = get_object_or_404(Menu, pk=menu_id)
            menu_data = {
                "menu_id": menu.menu_id,
                "menu_name": menu.menu_name,
                "quick_path": menu.quick_path,
                "screen_name": menu.screen_name,
                "url": menu.url,
                "module_id": menu.module_id,
                "parent_menu_id": menu.parent_menu_id,
                "display_order": menu.display_order,
                "app_id": menu.app_id,
                "icon": menu.icon,
                "is_active": menu.is_active,
                "is_add": menu.is_add,
                "is_view": menu.is_view,
                "is_edit": menu.is_edit,
                "is_delete": menu.is_delete,
                "is_execute": menu.is_execute,
            }
            return JsonResponse(menu_data)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            menu_name = request.GET.get('menu_name', None)
            exists = Menu.objects.filter(menu_name=menu_name).exists()
            return JsonResponse({'exists': exists})

        menu_to_edit = None
        if (menu_id):
            menu_to_edit = Menu.objects.filter(menu_id=menu_id).first()

        menu_list = Menu.objects.filter(parent_menu_id="No Parent").order_by('-created_on').values('menu_name', 'menu_id')
        parent_menus = Menu.objects.values_list('menu_name', flat=True).distinct()
        fetch_details = Menu.objects.all().order_by('display_order')

        return render(request, self.template_name, {
            "menu_list": menu_list,
            "parent_menus": parent_menus,
            "fetch_details": fetch_details,
            "parent_menu_id": menu_to_edit.parent_menu_id if menu_to_edit else None,
        })

    
    def post(self, request):
        menu_id = request.POST.get('menu_id') 
        menu_name = request.POST.get('menu_name')
        quick_path = request.POST.get('quick_path')
        screen_name = request.POST.get('screen_name')
        url = request.POST.get('url')
        module_id = request.POST.get('module_id')
        parent_menu_id = request.POST.get('parent_menu_id')
        display_order = request.POST.get('display_order')
        instance_id = request.POST.get('instance_id', '1')
        buffer1 = request.POST.get('buffer1')
        buffer2 = request.POST.get('buffer2')
        buffer3 = request.POST.get('buffer3')
        is_active = "is_active" in request.POST
        is_add = "is_add" in request.POST
        is_view = "is_view" in request.POST
        is_edit = "is_edit" in request.POST
        is_delete = "is_delete" in request.POST
        is_execute = "is_execute" in request.POST
        app_id = request.POST.get('app_id')
        icon = request.POST.get('icon')
    
        if parent_menu_id and parent_menu_id != "No Parent":
            parent_menu = Menu.objects.filter(menu_id=parent_menu_id).first()
            if parent_menu:
                parent_menu_id = parent_menu.menu_id
            else:
                messages.error(request, "Invalid Parent Menu selected.")
                return redirect("menu_list")

        if menu_id: 
            menu = get_object_or_404(Menu, pk=menu_id)
            menu.menu_name = menu_name
            menu.quick_path = quick_path
            menu.screen_name = screen_name
            menu.url = url
            menu.module_id = module_id
            menu.parent_menu_id = parent_menu_id
            menu.display_order = display_order
            menu.instance_id = instance_id
            menu.buffer1 = buffer1
            menu.buffer2 = buffer2
            menu.buffer3 = buffer3
            menu.is_active = is_active
            menu.is_add = is_add
            menu.is_view = is_view
            menu.is_edit = is_edit
            menu.is_delete = is_delete
            menu.is_execute = is_execute
            menu.app_id = app_id
            menu.icon = icon
            menu.modified_by = 1
            menu.modified_on = now() 
            menu.save()
            messages.success(request, "Menu updated successfully!")
        else: 
            Menu.objects.create(
                comp_code="1000",
                menu_name=menu_name,
                quick_path=quick_path,
                screen_name=screen_name,
                url=url,
                module_id=module_id,
                parent_menu_id=parent_menu_id,
                display_order=display_order,
                instance_id="1",
                buffer1=buffer1,
                buffer2=buffer2,
                buffer3=buffer3,
                is_active=is_active,
                is_add=is_add,
                is_view=is_view,
                is_edit=is_edit,
                is_delete=is_delete,
                is_execute=is_execute,
                app_id=app_id,
                icon=icon,
                created_by=1,
                created_on=now(),
            )
            messages.success(request, "Menu created successfully!")
            
    

        return redirect("menu_list")
    
    def delete_menu(request):
        if request.method == "POST":
            menu_id = request.POST.get("menu_id")
            if menu_id:
                try:
                    menu = get_object_or_404(Menu, menu_id=menu_id)
                    menu.is_active = False
                    menu.save()
                    return JsonResponse({"success": True, "message": "Menu has been deactivated successfully."})
                except Exception as e:
                    return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

        return JsonResponse({"success": False, "message": "Invalid request method."})



from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Menu, RoleMenu
from security.models import RoleMaster
import json

def permission_view(request):
    role_name = request.GET.get('role_name', 'No role name provided')
    try:
        role = RoleMaster.objects.get(role_name=role_name)
    except RoleMaster.DoesNotExist:
        role = None

    active_menus = Menu.objects.filter(is_active=True)
    module_ids = Menu.objects.filter(is_active=True).values('module_id').distinct()

    context = {
        'role_name': role_name,
        'role_id': role.id if role else 'No role ID',
        'module_ids': module_ids,
    }
    return render(request, 'pages/security/role/permission.html', context)

@csrf_exempt
def update_role_menu(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received Data:", data)  # Debugging

            changes = data.get('changes')
            if not changes:
                return JsonResponse({'success': False, 'error': 'No changes provided'})

            for change in changes:
                role_id = change.get('role_id')
                menu_id = change.get('menu_id')
                permission = change.get('permission')
                is_checked = change.get('is_checked')

                if role_id and menu_id and permission is not None:
                    role_menu, created = RoleMenu.objects.get_or_create(role_id=role_id, menu_id=menu_id)
                    setattr(role_menu, permission, is_checked)
                    role_menu.save()
                    print(f"Updated RoleMenu: {role_menu.menu_id} {permission}={is_checked}")  # Debugging

            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error: {e}")  # Debugging
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_menus_by_module(request, module_id):
    
    try:
        role_id = request.GET.get('role_id')
        menus = Menu.objects.filter(module_id=module_id, is_active=True)
        menu_list = []

        for menu in menus:
            role_menu = RoleMenu.objects.filter(role_id=role_id, menu_id=menu.menu_id).first()
            menu_list.append({
                'menu_id': menu.menu_id,
                'menu_name': menu.menu_name,
                'is_add_enabled': menu.is_add,
                'is_edit_enabled': menu.is_edit,
                'is_view_enabled': menu.is_view,
                'is_delete_enabled': menu.is_delete,
                'is_add_checked': role_menu.add if role_menu else False,
                'is_edit_checked': role_menu.modify if role_menu else False,
                'is_view_checked': role_menu.view if role_menu else False,
                'is_delete_checked': role_menu.delete if role_menu else False,
            })

        return JsonResponse({'menus': menu_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ----- Company Master

def company_master(request):
    set_comp_code(request)
    template_name = "pages/payroll/company_master/company_list.html"
    companies = CompanyMaster.objects.filter(company_code=COMP_CODE).order_by('-created_on')
    count = CompanyMaster.objects.filter(company_code=COMP_CODE).count()
    return render(request, template_name, {'companies': companies, 'count': count})

def add_company(request):
    set_comp_code(request)
    if request.method == "POST":
        CompanyMaster.objects.create(
            company_code=COMP_CODE,
            company_name=request.POST.get("company_name"),
            company_status=request.POST.get("company_status"),
            inception_date=request.POST.get("inception_date"),
            currency_code=request.POST.get("currency_code"),
            country_code=request.POST.get("country_code"),
            labour_ministry_id=request.POST.get("labour_ministry_id"),
            labour_bank_acc_no=request.POST.get("labour_account_number"),
            image_url=request.FILES.get("image_url"),
            address_line1=request.POST.get("address_line1"),
            address_line2=request.POST.get("address_line2"),
            address_line_city=request.POST.get("address_line_city"),
            address_line_state=request.POST.get("address_line_state"),
            telephone1=request.POST.get("telephone1"),
            telephone2=request.POST.get("telephone2"),
            fax_number=request.POST.get("fax_number"),
            salary_roundoff=request.POST.get("salary_roundoff"),
            mail_id=request.POST.get("mail_id"),
            social_media_id=request.POST.get("social_media_id"),
            po_box=request.POST.get("po_box"),
            is_active=request.POST.get("is_active") == "Active",
            created_by=1,
        )
        return redirect('company_list')
    
    return redirect('company_list')

def company_edit(request):
    set_comp_code(request)
    if request.method == "GET":
        company_id = request.GET.get("company_id")
        try:
            company = get_object_or_404(CompanyMaster, company_id=int(company_id), company_code=COMP_CODE)
            return JsonResponse({
                "company_id": company.company_id,
                "company_code": company.company_code,
                "company_name": company.company_name,
                "inception_date": company.inception_date,
                "company_status": company.company_status,
                "labour_ministry_id": company.labour_ministry_id,
                "labour_bank_acc_no": company.labour_bank_acc_no,
                "image_url": f"{settings.MEDIA_URL}{company.image_url}" if company.image_url else "",
                "currency_code": company.currency_code,
                "address_line1": company.address_line1,
                "address_line2": company.address_line2,
                "address_line_city": company.address_line_city,
                "address_line_state": company.address_line_state,
                "country_code": company.country_code,
                "telephone1": company.telephone1,
                "telephone2": company.telephone2,
                "fax_number": company.fax_number,
                "mail_id": company.mail_id,
                "social_media_id": company.social_media_id,
                "instance_id": company.instance_id,
                "salary_roundoff": company.salary_roundoff,
                "po_box": company.po_box,
                "is_active": company.is_active
            })
        except Exception as e:
            print(f"Error in company_edit: {str(e)}")
            return JsonResponse({"error": "Company data not found."}, status=404)
        
    if request.method == "POST":
        comp_id = request.POST.get('company_id')
        try:
            company = get_object_or_404(CompanyMaster, company_id=int(comp_id), company_code=COMP_CODE)
            if 'image_url' in request.FILES:
                image_file = request.FILES['image_url']
                file_path = f'company_logos/{company.company_code}/{image_file.name}'
                company.image_url.save(file_path, image_file, save=True)

            company.company_code = request.POST.get('company_code', company.company_code)
            company.company_name = request.POST.get('company_name', company.company_name)
            company.inception_date = request.POST.get('inception_date', company.inception_date)
            company.company_status = request.POST.get('company_status', company.company_status)
            company.labour_ministry_id = request.POST.get('labour_ministry_id', company.labour_ministry_id)
            company.labour_bank_acc_no = request.POST.get('labour_bank_acc_no', company.labour_bank_acc_no)
            company.currency_code = request.POST.get('currency_code', company.currency_code)
            company.address_line1 = request.POST.get('address_line1', company.address_line1)
            company.address_line2 = request.POST.get('address_line2', company.address_line2)
            company.address_line_city = request.POST.get('address_line_city', company.address_line_city)
            company.address_line_state = request.POST.get('address_line_state', company.address_line_state)
            company.country_code = request.POST.get('country_code', company.country_code)
            company.telephone1 = request.POST.get('telephone1', company.telephone1)
            company.telephone2 = request.POST.get('telephone2', company.telephone2)
            company.fax_number = request.POST.get('fax_number', company.fax_number)
            company.mail_id = request.POST.get('mail_id', company.mail_id)
            company.social_media_id = request.POST.get('social_media_id', company.social_media_id)
            company.instance_id = request.POST.get('instance_id', company.instance_id)
            company.salary_roundoff = request.POST.get('salary_roundoff', company.salary_roundoff)
            company.po_box = request.POST.get('po_box', company.po_box)
            company.is_active = request.POST.get("is_active") == "Active"

            company.save()

            return redirect('company_list')

        except Exception as e:
            print(f"Error updating company data: {str(e)}")
            return JsonResponse({"error": "Error updating company data."}, status=500)

    return redirect('company_list')


def check_company_code(request):
    company_code = request.GET.get('company_code')
    exists = CompanyMaster.objects.filter(company_code=company_code).exists()
    return JsonResponse({"exists": exists})
def check_emp_code(request):
    emp_code = request.GET.get('emp_code', None)
    if emp_code:
        exists = Employee.objects.filter(emp_code=emp_code).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})

@csrf_exempt
def check_grade_code(request):
    if request.method == "POST":
        grade_code = request.POST.get("grade_code")
        comp_code = request.session.get("comp_code")
        exists = GradeMaster.objects.filter(grade_code=grade_code, comp_code=comp_code).exists()
        return JsonResponse({"exists": exists})
    return JsonResponse({"error": "Invalid request"}, status=400)



def attendance_upload(request):
    if request.method == 'POST':
        paycycle = request.POST.get('paycycle')
        excel_file = request.FILES.get('excel_file')
        
        if not paycycle:
            messages.error(request, "Paycycle is mandatory.")
            return redirect('attendance_upload')
        
        # Set paycycle in session
        request.session['paycycle'] = paycycle

        # Process the uploaded file
        if (excel_file):
            try:
                df = pd.read_excel(excel_file, engine='openpyxl')
                required_columns = ["S.No", "Emp Code", "Start Date", "End Date", "Project", "Attendance_type", "Morning", "Afternoon", "OT1", "OT2"]
                
                if all(column in df.columns for column in required_columns):
                    df['Error'] = ''  # Add a temporary column for error messages
                    error_data = []

                    for index, row in df.iterrows():
                        emp_code = row['Emp Code']
                        if not Employee.objects.filter(emp_code=emp_code, process_cycle=paycycle).exists():
                            df.at[index, 'Error'] += 'Invalid Emp Code for the selected paycycle. '
                        if row.isnull().any():
                            df.at[index, 'Error'] += 'Some columns are null. '

                        if df.at[index, 'Error']:
                            error_row = row.to_dict()
                            error_row['Error'] = df.at[index, 'Error']
                            error_data.append(error_row)

                    table_data = df[df['Error'] == ''].drop(columns=['Error']).astype(str).to_dict(orient='records')
                    error_data = pd.DataFrame(error_data).astype(str).to_dict(orient='records')

                    request.session['table_data'] = table_data
                    request.session['error_data'] = error_data
                    return redirect('attendance_upload')
                else:
                    messages.error(request, "Excel format is invalid. Please ensure all required columns are present.")
            except BadZipFile:
                messages.error(request, "The uploaded file is not a valid Excel file.")
    
    table_data = request.session.get('table_data', None)
    error_data = request.session.get('error_data', None)
    return render(request, 'pages/payroll/attendance_upload/attendance_upload.html', {
        'table_data': table_data,
        'error_data': error_data
    })

def upload_attendance_data(request):
    set_comp_code(request)
    if request.method == 'POST':
        paycycle = request.session.get('paycycle')
        table_data = request.session.get('table_data', [])
        print('table', table_data)

        if not paycycle:
            messages.error(request, "Paycycle is mandatory.")
            return redirect('attendance_upload')

        try:
            paycycle_master = PaycycleMaster.objects.get(comp_code=COMP_CODE, process_cycle=paycycle)
            vMonth = paycycle_master.pay_process_month
            vMaxHours = paycycle_master.hours_per_day
            vOTHrs = paycycle_master.max_ot1_hrs

            for row in table_data:
                start_date = datetime.strptime(row['Start Date'], '%Y-%m-%d')
                end_date = datetime.strptime(row['End Date'], '%Y-%m-%d')
                ot1 = float(row['OT1'])
                ot2 = float(row['OT2'])

                cur_date = start_date
                while cur_date <= end_date:
                    vOTHours = 0
                    vHoliday = HolidayMaster.objects.filter(comp_code=COMP_CODE, holiday_date=cur_date).count()

                    if vHoliday == 0 and ot2 > 0 and cur_date.strftime('%A') == 'Friday':
                        vHoliday = 1
                        ot2 -= 1

                    if vHoliday == 0 and ot1 > 0:
                        vOTHours = min(ot1, vOTHrs)
                        ot1 -= vOTHours

                    WorkerAttendanceRegister.objects.update_or_create(
                        comp_code=COMP_CODE,
                        employee_code=row['Emp Code'],
                        date=cur_date,
                        defaults={
                            'pay_cycle': paycycle,
                            'pay_process_month': vMonth,
                            'project_code': row['Project'],
                            'attendance_type': 26 if vHoliday == 0 else 28,
                            'morning': row['Morning'],
                            'afternoon': row['Afternoon'],
                            'ot1': vOTHours if vHoliday == 0 else 0,
                            'ot2': 0 if vHoliday == 0 else 8,
                            'is_active': True,
                            'created_by': request.user.id if request.user.is_authenticated else 1,
                            'created_on': now(),
                            'in_time': '08:00',
                            'out_time': '17:00'
                        }
                    )
                    cur_date += timedelta(days=1)

            messages.success(request, "Attendance data uploaded successfully.")
        except PaycycleMaster.DoesNotExist:
            messages.error(request, "Invalid paycycle.")
        except Exception as e:
            messages.error(request, f"Error uploading attendance data: {str(e)}")

        # Destroy the session variables if table_data has values
        if table_data:
            request.session.pop('paycycle', None)
            request.session.pop('table_data', None)
            request.session.pop('error_data', None)

    return redirect('attendance_upload')

def cancel_attendance_upload(request):
    if request.method == 'POST':
        request.session.pop('paycycle', None)
        request.session.pop('table_data', None)
        request.session.pop('error_data', None)
        messages.success(request, "Attendance upload process has been canceled.")
    return redirect('attendance_upload')

def payroll_processing(request):
    set_comp_code(request)
    if request.method == 'POST':
        paycycle = request.POST.get('paycycle')
        paymonth = request.POST.get('paymonth')
        status = request.POST.get('status')

        if not paycycle or not paymonth:
            messages.error(request, "Paycycle and Paymonth are mandatory.")
            return redirect('payroll_processing')

        # Process payroll logic here
        # ...

        messages.success(request, "Payroll processed successfully.")
        return redirect('payroll_processing')

    return render(request, 'pages/payroll/payroll_processing/payroll_processing.html')

def cancel_payroll_processing(request):
    if request.method == 'POST':
        # Logic to cancel payroll processing
        messages.success(request, "Payroll processing has been canceled.")
    return redirect('payroll_processing')

def fetch_paymonth(request):
    set_comp_code(request)
    paycycle = request.GET.get('paycycle')
    if paycycle:
        paycycle_master = PaycycleMaster.objects.filter(comp_code=COMP_CODE, process_cycle=paycycle).first()
        if paycycle_master:
            paymonths = [paycycle_master.pay_process_month]  # Example, modify as needed
            options = ''.join([f'<option value="{month}">{month}</option>' for month in paymonths])
            return JsonResponse({'options': options})
    return JsonResponse({'options': '<option value="">Select Paymonth</option>'})

# -----------------------------------------------------------------------------------------------------------------------------------------


from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views import View
from .models import AdvanceMaster
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AdvanceMasterList(View):
    template_name = "pages/payroll/advance_master/advance_master_list.html"

    def get(self, request, *args, **kwargs):
        context = {
            'contracts': AdvanceMaster.objects.filter(comp_code='1000'),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        advance_id = data.get('advance_id')  # Fetch the advance_id from the form
        try:
            # Process date fields
            reference_date = datetime.strptime(data.get('reference_date'), '%d-%m-%Y').date()
            repayment_from = datetime.strptime(data.get('repayment_from'), '%d-%m-%Y').date()
            next_repayment_date = datetime.strptime(data.get('next_repayment_date'), '%d-%m-%Y').date()
            waiver_date = datetime.strptime(data.get('waiver_date'), '%d-%m-%Y').date() if data.get('waiver_date') else None
        except ValueError:
            return self.render_with_error(request, "Invalid date format. Please use DD-MM-YYYY.")

        # Prepare the data
        advance_data = {
            'comp_code': '1000',
            'emp_code': data.get('emp_code'),
            'advance_code': data.get('advance_code'),
            'advance_reference': data.get('advance_reference'),
            'reference_date': reference_date,
            'total_amt': data.get('total_amt'),
            'instalment_amt': data.get('instalment_amt'),
            'paid_amt': data.get('paid_amt'),
            'total_no_instalment': data.get('total_no_instalment'),
            'balance_no_instalment': data.get('balance_no_instalment'),
            'repayment_from': repayment_from,
            'next_repayment_date': next_repayment_date,
            'default_count': data.get('default_count'),
            'waiver_amt': data.get('waiver_amt'),
            'waiver_date': waiver_date,
            'is_active': data.get('is_active') == 'true',
            'modified_by': '1',
            'created_by': '1',
        }

        try:
            if advance_id:  # If advance_id is provided, update the record
                advance_master = AdvanceMaster.objects.get(advance_id=advance_id)
                for key, value in advance_data.items():
                    setattr(advance_master, key, value)
                advance_master.save()
                message = "Record updated successfully!"
            else:  # If no advance_id, create a new record
                AdvanceMaster.objects.create(**advance_data)
                message = "Record created successfully!"
            
            return redirect('advance_master')  # Redirect to the Advance Master list
        except AdvanceMaster.DoesNotExist:
            return self.render_with_error(request, "Record not found for the provided Advance ID.")
        except Exception as e:
            logger.error("Error saving advance master: %s", e)
            return self.render_with_error(request, "An error occurred while saving the data.")

    def render_with_error(self, request, error_message):
        context = {
            'error_message': error_message,
            'contracts': AdvanceMaster.objects.filter(comp_code='1000', is_active=True),
        }
        return render(request, self.template_name, context)

@csrf_exempt
def toggle_active_status(request, advance_id):
    if request.method == "POST":
        try:
            # Fetch the record by ID
            record = AdvanceMaster.objects.get(advance_id=advance_id)

            # Mark as inactive
            record.is_active = False
            record.save()

            return JsonResponse({"success": True, "message": "Status updated to Inactive."})
        except AdvanceMaster.DoesNotExist:
            return JsonResponse({"success": False, "message": "Record not found."}, status=404)
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)


logger = logging.getLogger(__name__)

@csrf_exempt
def get_advance_details(request, advance_id):
    try:
        advance = AdvanceMaster.objects.get(advance_id=advance_id)
        data = {
            'advance_id': advance.advance_id,
            'emp_code': advance.emp_code,
            'advance_code': advance.advance_code,
            'advance_reference': advance.advance_reference,
            'reference_date': advance.reference_date.strftime('%d-%m-%Y'),
            'total_amt': advance.total_amt,
            'instalment_amt': advance.instalment_amt,
            'paid_amt': advance.paid_amt,
            'total_no_instalment': advance.total_no_instalment,
            'balance_no_instalment': advance.balance_no_instalment,
            'repayment_from': advance.repayment_from.strftime('%d-%m-%Y'),
            'next_repayment_date': advance.next_repayment_date.strftime('%d-%m-%Y'),
            'default_count': advance.default_count,
            'waiver_amt': advance.waiver_amt,
            'waiver_date': advance.waiver_date.strftime('%d-%m-%Y') if advance.waiver_date else '',
            'is_active': advance.is_active,
        }
        return JsonResponse(data)
    except AdvanceMaster.DoesNotExist:
        return JsonResponse({'error': 'Record not found!'}, status=404)

@csrf_exempt
def update_advance_details(request, advance_id):
    if request.method == 'POST':
        try:
            advance = get_object_or_404(AdvanceMaster, advance_id=advance_id)
            data = request.POST

            # Update fields with validation
            advance.comp_code = '1000'
            advance.emp_code = data.get('emp_code')
            advance.advance_code = data.get('advance_code')
            advance.advance_reference = data.get('advance_reference')

            # Handle date fields
            reference_date = data.get('reference_date')
            repayment_from = data.get('repayment_from')
            next_repayment_date = data.get('next_repayment_date')
            waiver_date = data.get('waiver_date')

            advance.reference_date = datetime.strptime(reference_date, '%d-%m-%Y').date() if reference_date else None
            advance.repayment_from = datetime.strptime(repayment_from, '%d-%m-%Y').date() if repayment_from else None
            advance.next_repayment_date = datetime.strptime(next_repayment_date, '%d-%m-%Y').date() if next_repayment_date else None
            advance.waiver_date = datetime.strptime(waiver_date, '%d-%m-%Y').date() if waiver_date else None

            # Handle other fields
            advance.total_amt = data.get('total_amt')
            advance.instalment_amt = data.get('instalment_amt')
            advance.paid_amt = data.get('paid_amt')
            advance.total_no_instalment = data.get('total_no_instalment')
            advance.balance_no_instalment = data.get('balance_no_instalment')
            advance.default_count = data.get('default_count')
            advance.waiver_amt = data.get('waiver_amt')
            advance.is_active = data.get('is_active') == 'true'

            advance.save()
            return JsonResponse({'success': True, 'message': 'Record updated successfully!'})
        except Exception as e:
            logger.error(f"Error updating AdvanceMaster with ID {advance_id}: {e}")
            return JsonResponse({'success': False, 'message': 'An error occurred while updating!'})
    return JsonResponse({'success': False, 'message': 'Invalid request method!'})




