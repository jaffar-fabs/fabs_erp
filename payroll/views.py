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
from itertools import zip_longest

PAGINATION_SIZE = 6

# Single import statement for models
from .models import *

# Initialize COMP_CODE globally
COMP_CODE = None

def set_comp_code(request):
    global COMP_CODE
    global PAY_CYCLES

    COMP_CODE = request.session.get("comp_code")
    pay_cycles_raw = request.session.get("user_paycycles", "")

    # Split pay cycles by ":" if it's a string, default to empty list
    PAY_CYCLES = pay_cycles_raw.split(":") if isinstance(pay_cycles_raw, str) else []

# -----Leave Master

def create_leave_master(request):
    if request.method == 'POST':
        # Get data from the POST request
        leave_code = request.POST.get('leave_code')
        leave_description = request.POST.get('leave_description')
        work_month = request.POST.get('work_month')
        eligible_days = request.POST.get('eligible_days')
        eligible_day_type = request.POST.get('eligible_day_type')
        payment_type = request.POST.get('payment_type')
        frequency = request.POST.get('frequency')
        gender = request.POST.get('gender')
        grade = request.POST.get('grade')
        carry_forward = request.POST.get('carry_forward') == 'on'  # Checkbox field
        carry_forward_period = request.POST.get('carry_forward_period')
        encashment = request.POST.get('encashment') == 'on'  # Checkbox field

        # Save data to the database
        LeaveMaster.objects.create(
            leave_code=leave_code,
            leave_description=leave_description,
            work_month=int(work_month),
            eligible_days=int(eligible_days),
            eligible_day_type=eligible_day_type,
            payment_type=payment_type,
            frequency=frequency,
            gender=gender,
            grade=grade if grade else None,
            carry_forward=carry_forward,
            carry_forward_period=int(carry_forward_period) if carry_forward_period else 0,
            encashment=encashment
        )
        # Redirect to the leave master list
        return redirect('leavemaster')

    # Render the template for GET request
    return render(request, 'pages/payroll/leave_master/leavemaster.html')

def leave_master_list(request):
    # Fetch all leave records to display in the list
    leavemaster = LeaveMaster.objects.all()
    return render(request, 'pages/payroll/leave_master/leavemaster.html', {'leavemaster': leavemaster})

def delete_leavemaster(request, pk):
    if request.method == 'POST':
        record = get_object_or_404(LeaveMaster, pk=pk)
        record.delete()
        return JsonResponse({'success': True})  # Return JSON response
    return JsonResponse({'success': False}, status=400)
# -----Leave Master


def employee_master(request):
    set_comp_code(request)
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)
    get_url = request.get_full_path()

    # Adjust URL for pagination
    if '?keyword' in get_url:
        get_url = get_url.split('&page=')[0]
        current_url = f"{get_url}&"
    else:
        get_url = get_url.split('?')[0]
        current_url = f"{get_url}?"

    # Initialize the query
    query = Employee.objects.filter(comp_code=COMP_CODE, process_cycle__in=PAY_CYCLES)

    # Apply search filter if a keyword is provided
    if keyword:
        try:
            query = query.filter(
                Q(emp_code__icontains=keyword) |
                Q(emp_name__icontains=keyword) |
                Q(surname__icontains=keyword) |
                Q(department__icontains=keyword)
            )
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

    # Apply pagination
    paginator = Paginator(query.order_by('emp_code'), PAGINATION_SIZE)

    try:
        employees_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        employees_page = paginator.page(1)
    except EmptyPage:
        employees_page = paginator.page(paginator.num_pages)

    # Fetch documents and earnings/deductions for each employee
    for employee in employees_page:
        employee.documents = EmployeeDocument.objects.filter(emp_code=employee.emp_code, relationship__isnull=True, document_number__isnull=True)
        employee.earn_deducts = EarnDeductMaster.objects.filter(comp_code=COMP_CODE, employee_code=employee.emp_code)
        employee.dependents = EmployeeDocument.objects.filter(emp_code=employee.emp_code, relationship__isnull=False)
        employee.license_and_passes = EmployeeDocument.objects.filter(emp_code=employee.emp_code, relationship__isnull=True,issued_date__isnull=True)

    # Prepare the context for the template
    context = {
        'employees': employees_page,
        'current_url': current_url,
        'keyword': keyword,
        'result_cnt': query.count()
    }

    return render(request, 'pages/payroll/employee_master/employee_master.html', context)

def get_employee_details(request, employee_id):
    set_comp_code(request)

    try:
        # Fetch the employee details
        employee = Employee.objects.get(employee_id=employee_id, comp_code=COMP_CODE)

        # Fetch related data
        documents = EmployeeDocument.objects.filter(emp_code=employee.emp_code, relationship__isnull=True, document_number__isnull=True)
        earn_deducts = EarnDeductMaster.objects.filter(comp_code=COMP_CODE, employee_code=employee.emp_code)
        dependents = EmployeeDocument.objects.filter(emp_code=employee.emp_code, relationship__isnull=False)
        license_and_passes = EmployeeDocument.objects.filter(emp_code=employee.emp_code, relationship__isnull=True, issued_date__isnull=True)

        # Prepare the context
        context = {
            'employee': employee,
            'documents': documents,
            'earn_deducts': earn_deducts,
            'dependents': dependents,
            'license_and_passes': license_and_passes,
        }

        return render(request, 'pages/modal/payroll/employee_master_modal.html', context)

    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)

def save_employee(request, employee_id=None):
    set_comp_code(request)
    if request.method == "POST":
        emp_code = request.POST.get("emp_code")
        
        # Check if emp_code already exists for new employees
        if not employee_id and Employee.objects.filter(emp_code=emp_code, comp_code=COMP_CODE).exists():
            messages.error(request, "Employee Code already exists.")
            return redirect('/employee')

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
        employee.emp_code = emp_code
        employee.emp_name = request.POST.get("emp_name_passport")
        employee.surname = request.POST.get("surname")
        employee.dob = request.POST.get("dob") or None
        employee.emp_sex = request.POST.get("emp_sex")
        employee.emp_status = request.POST.get("emp_status")
        employee.emp_sub_status = request.POST.get("emp_sub_status")
        employee.passport_release = request.POST.get("passport_release")
        employee.release_reason = request.POST.get("release_reason")
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
        employee.prj_code = request.POST.get("prj_code")
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

        # Additional details
        employee.passport_details = request.POST.get("passport_details")
        employee.passport_issued_country = request.POST.get("passport_issued_country")
        employee.passport_place_of_issue = request.POST.get("passport_place_of_issue")
        employee.issued_date = request.POST.get("issued_date") or None
        employee.expiry_date = request.POST.get("expiry_date") or None
        employee.iloe_no = request.POST.get("iloe_no")
        employee.iloe_expiry = request.POST.get("iloe_expiry") or None
        employee.iloe_document = request.FILES.get("iloe_document") or employee.iloe_document
        employee.visa_location = request.POST.get("visa_location")
        employee.visa_no = request.POST.get("visa_no")
        employee.emirates_no = request.POST.get("emirates_no")
        employee.visa_issued = request.POST.get("visa_issued") or None
        employee.visa_expiry = request.POST.get("visa_expiry") or None
        employee.emirate_issued = request.POST.get("emirate_issued") or None
        employee.emirate_expiry = request.POST.get("emirate_expiry") or None
        employee.uid_number = request.POST.get("uid_number")
        employee.mohra_number = request.POST.get("mohra_number")
        employee.mohra_name = request.POST.get("mohra_name")
        employee.mohra_designation = request.POST.get("mohra_designation")
        employee.work_permit_number = request.POST.get("work_permit_number")
        employee.work_permit_expiry = request.POST.get("work_permit_expiry") or None

        employee.labor_contract_issued_date = request.POST.get("labor_contract_issued_date") or None
        employee.labor_contract_expiry_date = request.POST.get("labor_contract_expiry_date") or None
        employee.emirates_id_issued_date = request.POST.get("emirates_id_issued_date") or None
        employee.emirates_id_expiry_date = request.POST.get("emirates_id_expiry_date") or None
        employee.visa_issued_date = request.POST.get("visa_copy_issued_date") or None
        employee.visa_expiry_date = request.POST.get("visa_copy_expiry_date") or None
        employee.passport_issued_date = request.POST.get("passport_copy_issued_date") or None
        employee.passport_expiry_date = request.POST.get("passport_copy_expiry_date") or None

        # Camp Details
        employee.camp_type = request.POST.get("camp_type")
        employee.camp_inside_outside = request.POST.get("camp_inside_outside")

        # Handle accommodation details based on the selected type
        if employee.camp_inside_outside == "client_accommodation":
            employee.client_name = request.POST.get("client_name")  # New field for Client Name
            employee.client_location = request.POST.get("client_location")  # New field for Client Location
        elif employee.camp_inside_outside == "camp":
            employee.select_camp = request.POST.get("select_camp")
            employee.room_no = request.POST.get("room_no")
        elif employee.camp_inside_outside == "outside":
            employee.outside_location = request.POST.get("outside_location")
            employee.room_rent = request.POST.get("room_rent")

        # Save employee
        employee.save()

        # Handle Earn/Deduct entries
        earn_deduct_types = request.POST.getlist("entry_type[]")
        earn_deduct_codes = request.POST.getlist("entry_code[]")
        earn_deduct_amounts = request.POST.getlist("entry_amount[]")
        prorated_flags = request.POST.getlist("entry_proated_flag[]")
        # Delete existing entries for the employee
        EarnDeductMaster.objects.filter(
            comp_code=COMP_CODE,
            employee_code=emp_code
        ).delete()  # Remove all existing entries for this employee

        # Create new entries
        for entry_type, entry_code, entry_amount, prorated_flag in zip(earn_deduct_types, earn_deduct_codes, earn_deduct_amounts, prorated_flags):
            if entry_type and entry_code and entry_amount:  # Ensure all fields are provided
                EarnDeductMaster.objects.create(
                    comp_code=COMP_CODE,
                    employee_code=emp_code,
                    earn_deduct_code=entry_code,
                    earn_deduct_amt=entry_amount,
                    prorated_flag=prorated_flag == 'Yes',  # Convert to boolean
                    created_by=1,  # Replace with actual user ID if available
                    instance_id=employee_id or emp_code,  # Use employee_id if editing, otherwise use emp_code
                    earn_type=entry_type
                )

        # Handle document removal
        documents_to_remove = request.POST.get('documents_to_remove', '').split(',')
        documents_to_remove = [doc_id for doc_id in documents_to_remove if doc_id.isdigit()]  # Filter valid IDs

        for doc_id in documents_to_remove:
            try:
                document = EmployeeDocument.objects.get(document_id=doc_id)
                if document.document_file:
                    file_path = document.document_file.path
                    if os.path.exists(file_path):
                        os.remove(file_path)  # Delete the file from the filesystem
                document.delete()
            except EmployeeDocument.DoesNotExist:
                continue

        # Handle new document uploads
        document_types = request.POST.getlist("document_type[]")
        document_files = request.FILES.getlist("document_file[]")

        # Save new documents to the database
        for doc_type, doc_file in zip(document_types, document_files):
            if doc_type and doc_file:  # Ensure both type and file are provided
                print(doc_type,doc_file)
                EmployeeDocument.objects.create(
                    comp_code=COMP_CODE,
                    emp_code=employee.emp_code,
                    document_type=doc_type,
                    document_file=doc_file,
                    created_by=1,  # Replace with actual user ID if available
                )

        # Handle dependent details
        dependent_relationships = request.POST.getlist("dependent_relationship[]")
        dependent_doc_types = request.POST.getlist("dependent_doc_type[]")
        dependent_doc_numbers = request.POST.getlist("dependent_doc_number[]")
        dependent_issued_dates = request.POST.getlist("dependent_issued_date[]")
        dependent_expiry_dates = request.POST.getlist("dependent_expiry_date[]")
        dependent_doc_files = request.FILES.getlist("dependent_doc_file[]")

        # Create new dependent entries
        

        for relationship, doc_type, doc_number, issued_date, expiry_date, doc_file in zip_longest(
                dependent_relationships, dependent_doc_types, dependent_doc_numbers,
                dependent_issued_dates, dependent_expiry_dates, dependent_doc_files):
            print(relationship, doc_type, doc_number, issued_date, expiry_date, doc_file)

            
            if relationship and doc_type and doc_number:  # Ensure required fields are provided
                EmployeeDocument.objects.create(
                    comp_code=COMP_CODE,
                    emp_code=employee.emp_code,
                    relationship=relationship,
                    document_type=doc_type,
                    document_number=doc_number,
                    issued_date=issued_date,
                    expiry_date=expiry_date,
                    document_file=doc_file if doc_file else None,  # Save file if provided
                    created_by=1,  # Replace with actual user ID if available
                )

        # Handle License and Passes Details
        license_doc_types = request.POST.getlist("license_doc_type[]")
        license_doc_numbers = request.POST.getlist("license_doc_number[]")
        license_doc_files = request.FILES.getlist("license_doc_file[]")
        license_work_locations = request.POST.getlist("work_location[]")
        license_emirates_issued = request.POST.getlist("emirate_issued[]")
        license_expiry_dates = request.POST.getlist("license_expiry_date[]")
        license_categories = request.POST.getlist("license_category[]")
        license_comments = request.POST.getlist("license_comments[]")

        print(license_doc_types, license_doc_numbers, license_doc_files,
                license_work_locations, license_emirates_issued, license_expiry_dates, license_categories, license_comments)

        for doc_type, doc_number, doc_file, work_location, emirate_issued, expiry_date, category, comments in zip_longest(
                license_doc_types, license_doc_numbers, license_doc_files,
                license_work_locations, license_emirates_issued,
                license_expiry_dates, license_categories, license_comments):

            print(doc_type, doc_number, doc_file, work_location, emirate_issued, expiry_date, category, comments)

            if doc_type and doc_number:
                # Create document entry (adjust model and field names as needed)
                EmployeeDocument.objects.create(
                    comp_code=COMP_CODE,
                    emp_code=employee.emp_code,
                    document_type=doc_type,
                    document_number=doc_number,
                    document_file=doc_file if doc_file else None,
                    staff_work_location=work_location,
                    emirates_issued_by=emirate_issued,
                    expiry_date=expiry_date,
                    category=category,
                    comments=comments,
                    created_by=request.user.id if request.user.is_authenticated else 1
                )



        # Continue with the rest of your code
        messages.success(request, "Employee details and documents updated successfully.")
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

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
    project_count = projectMaster.objects.filter(comp_code=COMP_CODE).count()
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
                request.session["user_paycycles"] = user.user_paycycles

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
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)
    get_url = request.get_full_path()

    # Adjust URL for pagination
    if '?keyword' in get_url:
        get_url = get_url.split('&page=')[0]
        current_url = f"{get_url}&"
    else:
        get_url = get_url.split('?')[0]
        current_url = f"{get_url}?"

    # Initialize the query
    query = SeedModel.objects.filter(comp_code=COMP_CODE)

    # Apply search filter if a keyword is provided
    if keyword:
        try:
            query = query.filter(
                Q(seed_code__icontains=keyword) |
                Q(seed_group__icontains=keyword) |
                Q(seed_type__icontains=keyword)
            )
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

    # Apply pagination
    paginator = Paginator(query.order_by('seed_code'), PAGINATION_SIZE)

    try:
        seeds_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        seeds_page = paginator.page(1)
    except EmptyPage:
        seeds_page = paginator.page(paginator.num_pages)

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

    # Prepare the context for the template
    context = {
        'seed_data': seeds_page,
        'current_url': current_url,
        'keyword': keyword,
        'result_cnt': query.count()
    }

    return render(request, 'pages/payroll/seed_master/seedmaster.html', context)

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
        keyword = request.GET.get('keyword', '').strip()
        page_number = request.GET.get('page', 1)
        get_url = request.get_full_path()

        # Adjust URL for pagination
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        # Initialize the query
        query = PaycycleMaster.objects.filter(comp_code=COMP_CODE)

        # Apply search filter if a keyword is provided
        if keyword:
            try:
                query = query.filter(
                    Q(process_cycle__icontains=keyword) |
                    Q(process_description__icontains=keyword) |
                    Q(pay_process_month__icontains=keyword)
                )
            except Exception as e:
                print(f"Error in keyword search: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

        # Apply pagination
        paginator = Paginator(query.order_by('-created_on'), PAGINATION_SIZE)

        try:
            paycycle_page = paginator.get_page(page_number)
        except PageNotAnInteger:
            paycycle_page = paginator.page(1)
        except EmptyPage:
            paycycle_page = paginator.page(paginator.num_pages)

        # Prepare the context for the template
        context = {
            "paycycle_list": paycycle_page,
            "current_url": current_url,
            "keyword": keyword,
            "result_cnt": query.count()
        }

        return render(request, self.template_name, context)

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
        ot1_amt = request.POST.get('ot1_amt') or 0
        max_ot2_hrs = request.POST.get('max_ot2_hrs')
        ot2_amt = request.POST.get('ot2_amt') or 0
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
        return num - 1

    project_id = request.GET.get("project_id")
    print(project_id, 'project_id')
    
    if request.method == "GET":
        if project_id:  # If `project_id` exists, return a JSON response with project data
            try:
                project = projectMaster.objects.get(project_id=project_id, comp_code=COMP_CODE)
                return JsonResponse({
                    "project_id": project.project_id,
                    "prj_code": project.prj_code,
                    "prj_name": project.prj_name,
                    "project_description": project.project_description,
                    "project_type": project.project_type,
                    "project_value": project.project_value,
                    "timeline_from": project.timeline_from,
                    "timeline_to": project.timeline_to,
                    "prj_city": project.prj_city.split(':') if project.prj_city else [], 
                    "is_active": project.is_active,
                    "comp_code": project.comp_code,
                    "service_type": project.service_type.split(':') if project.service_type else [], 
                    "service_category": project.service_category.split(':') if project.service_category else [],
                    "pro_sub_location": project.pro_sub_location.split(':') if project.pro_sub_location else [],
                    "customer": project.customer,
                    "agreement_ref": project.agreement_ref,
                    "op_head": project.op_head,
                    "manager": project.manager,
                    "commercial_manager": project.commercial_manager,
                    "procurement_user": project.procurement_user,
                    "indent_user": project.indent_user,
                    "final_contract_value": project.final_contract_value or 0,
                    "project_status": project.project_status,
                })
            except projectMaster.DoesNotExist:
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
            query = projectMaster.objects.filter(comp_code=COMP_CODE)

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
                    "is_active": project.is_active,
                    "comp_code": project.comp_code,
                    "service_type": project.service_type,
                    "service_category": project.service_category,
                    "pro_sub_location": project.pro_sub_location,
                    "op_head": project.op_head,
                    "manager": project.manager,
                    "commercial_manager": project.commercial_manager,
                    "procurement_user": project.procurement_user,
                    "indent_user": project.indent_user,
                    "customer": project.customer,
                    "agreement_ref": project.agreement_ref,
                    "project_status": project.project_status,
                    "final_contract_value": project.final_contract_value
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

        # Get prj_city from the POST request
        prj_city = request.POST.getlist('prj_city')  # Get list of selected cities
        prj_city_str = ':'.join(prj_city)  # Convert list to colon-separated string

        if projectMaster.objects.filter(project_id=project_id, comp_code=COMP_CODE).exists():
            project = get_object_or_404(projectMaster, project_id=int(project_id), comp_code=COMP_CODE)

            project.prj_code = request.POST.get("project_code", project.prj_code)
            project.prj_name = request.POST.get("project_name", project.prj_name)
            project.project_description = request.POST.get("project_description", project.project_description)
            project.project_type = request.POST.get("project_type", project.project_type)
            project.project_value = request.POST.get("project_value", project.project_value)
            project.timeline_from = request.POST.get("timeline_from", project.timeline_from)
            project.timeline_to = request.POST.get("timeline_to", project.timeline_to)
            project.prj_city = prj_city_str  # Save the prj_city string
            project.is_active = request.POST.get("is_active") == "Active"
            project.created_by = 1
            project.comp_code = request.POST.get("comp_code", project.comp_code)
            project.service_type = request.POST.get("service_type", project.service_type)
            project.service_category = request.POST.get("service_category", project.service_category)
            project.pro_sub_location = request.POST.get("pro_sub_location", project.pro_sub_location)
            project.op_head = request.POST.get("op_head", project.op_head)
            project.manager = request.POST.get("manager", project.manager)
            project.commercial_manager = request.POST.get("commercial_manager", project.commercial_manager)
            project.procurement_user = request.POST.get("procurement_user", project.procurement_user)
            project.indent_user = request.POST.get("indent_user", project.indent_user)
            project.customer = request.POST.get("customer", project.customer)
            project.agreement_ref = request.POST.get("agreement_ref", project.agreement_ref)
            project.final_contract_value = request.POST.get("final_contract_value", project.final_contract_value)
            project.project_status = request.POST.get("project_status", project.project_status)

            project.save()
            return redirect("project")

        else:
            prj_code = request.POST.get("project_code")
            project = projectMaster(
                prj_code=request.POST.get("project_code"),
                prj_name=request.POST.get("project_name"),
                project_description=request.POST.get("project_description", "No description available"),
                project_type=request.POST.get("project_type", 0),
                project_value=request.POST.get("project_value", 0.00),
                timeline_from=request.POST.get("timeline_from", "Not specified"),
                timeline_to=request.POST.get("timeline_to", "Not specified"),
                prj_city=prj_city_str,  # Save the prj_city string
                created_by=1,
                is_active=request.POST.get("is_active") == "Active",
                comp_code=COMP_CODE,
                service_type=request.POST.get("service_type"),
                service_category=request.POST.get("service_category"),
                pro_sub_location=request.POST.get("pro_sub_location"),
                op_head=request.POST.get("op_head"),
                manager=request.POST.get("manager"),
                commercial_manager=request.POST.get("commercial_manager"),
                procurement_user=request.POST.get("procurement_user"),
                indent_user=request.POST.get("indent_user"),
                customer=request.POST.get("customer"),
                agreement_ref=request.POST.get("agreement_ref"),
                project_status=request.POST.get("project_status"),
                final_contract_value=request.POST.get("final_contract_value") or 0.00,
            )
            project.save()
        return redirect("project")

    return render(request, template_name, context=context)

def check_project_code(request):
    set_comp_code(request)
    if request.method == "POST":
        project_code = request.POST.get("project_code")

        if projectMaster.objects.filter(prj_code=project_code, comp_code=COMP_CODE).exists():
            return JsonResponse({"exists": True})  # Project code exists
        else:
            return JsonResponse({"exists": False})  # Project code is unique

    return JsonResponse({"error": "Invalid request"}, status=400)


def delete_project(request):
    set_comp_code(request)
    if request.method == "POST":
        project_id = request.POST.get("project_id")

        if project_id:
            project = get_object_or_404(projectMaster, project_id=project_id, comp_code=COMP_CODE)
            project.is_active = False  
            project.save()
    return redirect("project")

# Holiday Master -------------------------

# class HolidayMaster(View):


class CodeMasterList(View):
    template_name = "pages/payroll/code_master/code_master_list.html"

    def get(self, request):
        set_comp_code(request)
        keyword = request.GET.get('keyword', '').strip()
        page_number = request.GET.get('page', 1)
        get_url = request.get_full_path()

        # Adjust URL for pagination
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        # Initialize the query
        query = CodeMaster.objects.filter(comp_code="999")

        # Apply search filter if a keyword is provided
        if keyword:
            try:
                query = query.filter(
                    Q(base_value__icontains=keyword) |
                    Q(base_description__icontains=keyword)
                )
            except Exception as e:
                print(f"Error in keyword search: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

        # Apply pagination
        paginator = Paginator(query.order_by('base_value'), PAGINATION_SIZE)

        try:
            base_type_page = paginator.get_page(page_number)
        except PageNotAnInteger:
            base_type_page = paginator.page(1)
        except EmptyPage:
            base_type_page = paginator.page(paginator.num_pages)

        # Prepare the context for the template
        context = {
            "base_type_suggestions" : CodeMaster.objects.filter(comp_code="999").values("base_description", "base_value").distinct(),
            "base_type_comp_code": base_type_page,
            "current_url": current_url,
            "keyword": keyword,
            "result_cnt": query.count()
        }

        return render(request, self.template_name, context)

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
        set_comp_code(request)
        keyword = request.GET.get('keyword', '').strip()
        page_number = request.GET.get('page', 1)
        get_url = request.get_full_path()

        # Adjust URL for pagination
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        # Initialize the query
        query = UserMaster.objects.filter(comp_code=COMP_CODE)

        # Apply search filter if a keyword is provided
        if keyword:
            try:
                query = query.filter(
                    Q(user_id__icontains=keyword) |
                    Q(first_name__icontains=keyword) |
                    Q(last_name__icontains=keyword) |
                    Q(email__icontains=keyword)
                )
            except Exception as e:
                print(f"Error in keyword search: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

        # Apply pagination
        paginator = Paginator(query.order_by('user_id'), PAGINATION_SIZE)

        try:
            users_page = paginator.get_page(page_number)
        except PageNotAnInteger:
            users_page = paginator.page(1)
        except EmptyPage:
            users_page = paginator.page(paginator.num_pages)

        # Prepare the context for the template
        context = {
            'users': users_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': query.count()
        }

        return render(request, self.template_name, context)

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
            user_paycycles = request.POST.getlist('user_paycycles')  # Get list of selected paycycles
            user_paycycles_str = ':'.join(user_paycycles)  # Convert list to colon-separated string

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
                user_paycycles=user_paycycles_str  # Save as colon-separated string
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
            user.instance_id = 100000000
            user.profile_picture = request.FILES.get('profile_picture')
            user.modified_by = request.POST.get('modified_by')
            user.emp_code = request.POST.get('emp_code')
            
            user_paycycles = request.POST.getlist('user_paycycles')  # Get list of selected paycycles
            user.user_paycycles = ':'.join(user_paycycles)  # Convert list to colon-separated string
            
            user.is_active = request.POST.get('is_active') == 'on'
            
            user.full_clean()
            user.save()

            return JsonResponse({'status': 'success', 'redirect_url': reverse('user_list')})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
class UserMasterDelete(View):
    def post(self, request, user_master_id):
        
        user = get_object_or_404(UserMaster, user_master_id=user_master_id, comp_code=COMP_CODE)
        
        user.is_active = False
        user.save()  
        
        return redirect('user_list')
    
from django.http import JsonResponse
from .models import Employee

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Employee

def get_employee_data(request, emp_code):
    try:
        employee = Employee.objects.get(emp_code=emp_code)
        data = {
            'first_name': employee.emp_name,
            'surname': employee.surname,
            'dob': employee.dob.strftime('%Y-%m-%d') if employee.dob else None,
            'gender': employee.emp_sex,
        }
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
        
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import GradeMaster
from django.utils.timezone import now

class GradeMasterList(View):
    template_name = "pages/payroll/grade_master/grade_master_list.html"

    # def get(self, request):
    #     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    #         grade_code = request.GET.get('grade_code', None)
    #         data = {
    #             'exists': GradeMaster.objects.filter(grade_code=grade_code, comp_code=COMP_CODE).exists()
    #         }
    #         print(data)
    #         return JsonResponse(data)

    #     datas = GradeMaster.objects.filter(comp_code=COMP_CODE)
    #     return render(request, self.template_name, {'datas': datas})
    
    
    
    def get(self, request):
        # Fetch all relevant data from the database
        datas = GradeMaster.objects.filter(comp_code=COMP_CODE).values(
            'grade_id',
            'grade_code',
            'grade_desc',
            'designation',
            'passage_amount_adult',
            'passage_amount_child',
            'allowance1',
            'allowance2',
            'allowance3',
            'is_active'
        )
        return render(request, "pages/payroll/grade_master/grade_master_list.html", {'datas': datas})


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

def holidayList(request):
    set_comp_code(request)
    template_name = "pages/payroll/holiday_master/holiday_list.html"
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)
    get_url = request.get_full_path()

    # Adjust URL for pagination
    if '?keyword' in get_url:
        get_url = get_url.split('&page=')[0]
        current_url = f"{get_url}&"
    else:
        get_url = get_url.split('?')[0]
        current_url = f"{get_url}?"

    # Initialize the query
    query = HolidayMaster.objects.filter(comp_code=COMP_CODE)

    # Apply search filter if a keyword is provided
    if keyword:
        try:
            query = query.filter(
                Q(holiday__icontains=keyword) |
                Q(holiday_type__icontains=keyword) |
                Q(holiday_description__icontains=keyword)
            )
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

    # Apply pagination
    paginator = Paginator(query.order_by('-created_on'), PAGINATION_SIZE)

    try:
        holidays_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        holidays_page = paginator.page(1)
    except EmptyPage:
        holidays_page = paginator.page(paginator.num_pages)

    # Prepare the context for the template
    context = {
        'holidays': holidays_page,
        'current_url': current_url,
        'keyword': keyword,
        'result_cnt': query.count(),
        'holidayTypes': CodeMaster.objects.filter(comp_code=COMP_CODE, base_type='HOLIDAY')
    }

    return render(request, template_name, context)
        

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


def delete_holiday(request):
    if request.method == "POST":
        id = request.POST.get("holiday_id")
        if id:
            holiday = get_object_or_404(HolidayMaster, unique_id=id, comp_code=COMP_CODE)
            holiday.is_active = False  
            holiday.save()
        return redirect("holiday_master")
    return redirect("holiday_master")


class MenuMaster(View):
    template_name = "pages/security/menu_master/menu_list.html"

    def get(self, request, menu_id=None):
        set_comp_code(request)
        keyword = request.GET.get('keyword', '').strip()
        page_number = request.GET.get('page', 1)
        get_url = request.get_full_path()

        # Adjust URL for pagination
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        # Initialize the query
        query = Menu.objects.filter(comp_code=COMP_CODE)

        # Apply search filter if a keyword is provided
        if keyword:
            try:
                query = query.filter(
                    Q(menu_name__icontains=keyword) |
                    Q(quick_path__icontains=keyword) |
                    Q(url__icontains=keyword)
                )
            except Exception as e:
                print(f"Error in keyword search: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

        # Apply pagination
        paginator = Paginator(query.order_by('display_order'), PAGINATION_SIZE)

        try:
            menus_page = paginator.get_page(page_number)
        except PageNotAnInteger:
            menus_page = paginator.page(1)
        except EmptyPage:
            menus_page = paginator.page(paginator.num_pages)

        # Handle AJAX request for menu details
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

        # Handle AJAX request to check if a menu name exists
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            menu_name = request.GET.get('menu_name', None)
            exists = Menu.objects.filter(menu_name=menu_name).exists()
            return JsonResponse({'exists': exists})

        # Prepare data for rendering the template
        menu_to_edit = None
        if menu_id:
            menu_to_edit = Menu.objects.filter(menu_id=menu_id).first()

        menu_list = Menu.objects.filter(parent_menu_id="No Parent").order_by('-created_on').values('menu_name', 'menu_id')
        parent_menus = Menu.objects.values_list('menu_name', flat=True).distinct()
        fetch_details = Menu.objects.all().order_by('display_order')

        context = {
            "menus": menus_page,
            "menu_list": menu_list,
            "parent_menus": parent_menus,
            "fetch_details": fetch_details,
            "parent_menu_id": menu_to_edit.parent_menu_id if menu_to_edit else None,
            "current_url": current_url,
            "keyword": keyword,
            "result_cnt": query.count(),
        }

        return render(request, self.template_name, context)

    
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
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)
    get_url = request.get_full_path()

    # Adjust URL for pagination
    if '?keyword' in get_url:
        get_url = get_url.split('&page=')[0]
        current_url = f"{get_url}&"
    else:
        get_url = get_url.split('?')[0]
        current_url = f"{get_url}?"

    # Initialize the query
    if request.session.get('username') == "SYSTEM":
        query = CompanyMaster.objects.all()
    else:
        query = CompanyMaster.objects.filter(company_code=COMP_CODE)

    # Apply search filter if a keyword is provided
    if keyword:
        try:
            query = query.filter(
                Q(company_code__icontains=keyword) |
                Q(company_name__icontains=keyword)
            )
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

    # Apply pagination
    paginator = Paginator(query.order_by('-created_on'), PAGINATION_SIZE)

    try:
        companies_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        companies_page = paginator.page(1)
    except EmptyPage:
        companies_page = paginator.page(paginator.num_pages)

    # Prepare the context for the template
    context = {
        'companies': companies_page,
        'current_url': current_url,
        'keyword': keyword,
        'result_cnt': query.count()
    }

    return render(request, template_name, context)

def add_company(request):
    set_comp_code(request)
    if request.method == "POST":
        CompanyMaster.objects.create(
            company_code=request.POST.get("company_code"),
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

        document_type = request.POST.getlist("document_type[]")
        document_number = request.POST.getlist("document_number[]")
        document_file = request.FILES.getlist("document_file[]")
        issued_by = request.POST.getlist("issued_by[]")
        issued_date = request.POST.getlist("issued_date[]")
        expiry_date = request.POST.getlist("expiry_date[]")
        status = request.POST.getlist("status[]")
        remarks = request.POST.getlist("remarks[]")
        print(document_type, document_number, document_file, issued_by, issued_date, expiry_date, status, remarks) 

        for document_type, document_number, document_file, issued_by, issued_date, expiry_date, status, remarks in zip(
            document_type, document_number, document_file, issued_by, issued_date, expiry_date, status, remarks):
            CompanyDocument.objects.create(
                company_code = request.POST.get("company_code"),
                document_type=document_type,
                document_number=document_number,
                document_file=document_file,
                issued_by=issued_by,
                issued_date=issued_date,
                expiry_date=expiry_date,
                status=status,
                remarks=remarks
            )
        return redirect('company_list')
    
    return redirect('company_list')

def company_edit(request):
    set_comp_code(request)
    if request.method == "GET":
        company_id = request.GET.get("company_id")
        try:
            company = get_object_or_404(CompanyMaster, company_id=int(company_id))
            company_documents = CompanyDocument.objects.filter(company_code=company.company_code)

            document_data = []

            for doc in company_documents:
                document_data.append({
                    "document_id": doc.company_id,
                    "document_type": doc.document_type,
                    "document_number": doc.document_number,
                    "issued_by": doc.issued_by,
                    "issued_date": doc.issued_date,
                    "expiry_date": doc.expiry_date,
                    "status": doc.status,
                    "remarks": doc.remarks,
                    "file_url": f"{settings.MEDIA_URL}{doc.document_file}" if doc.document_file else ""
                })

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
                "is_active": company.is_active,
                "documents": document_data
            })
        except Exception as e:
            print(f"Error in company_edit: {str(e)}")
            return JsonResponse({"error": "Company data not found."}, status=404)
        
    if request.method == "POST":
        comp_id = request.POST.get('company_id')
        try:
            company = get_object_or_404(CompanyMaster, company_id=int(comp_id))
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

            # Document update logic
            remove_ids = request.POST.getlist("remove_id[]")  
            document_ids = request.POST.getlist("document_id[]")  
            document_type = request.POST.getlist("document_type[]")
            document_number = request.POST.getlist("document_number[]")
            document_file = request.FILES.getlist("document_file[]")
            issued_by = request.POST.getlist("issued_by[]")
            issued_date = request.POST.getlist("issued_date[]")
            expiry_date = request.POST.getlist("expiry_date[]")
            status = request.POST.getlist("status[]")
            remarks = request.POST.getlist("remarks[]")
            
            for i in range(len(document_type)):
                doc_id = document_ids[i] if i < len(document_ids) else None
                file = document_file[i] if i < len(document_file) else None

                if len(remove_ids) > 0 and remove_ids[i] != "":
                    try:
                        doc = CompanyDocument.objects.get(company_id=remove_ids[i], company_code=company.company_code)
                        doc.delete()
                    except CompanyDocument.DoesNotExist:
                        print(f"Document with id {remove_ids[i]} not found.")

                if doc_id and doc_id != "" and doc_id != "undefined":  # Update existing document
                    try:
                        doc = CompanyDocument.objects.get(company_id=doc_id, company_code=company.company_code)
                        doc.document_type = document_type[i]
                        doc.document_number = document_number[i]
                        doc.issued_by = issued_by[i]
                        doc.issued_date = issued_date[i]
                        doc.expiry_date = expiry_date[i]
                        doc.status = status[i]
                        doc.remarks = remarks[i]
                        if file:
                            doc.document_file = file
                        doc.save()
                    except CompanyDocument.DoesNotExist:
                        print(f"Document with id {doc_id} not found.")
                else:  # New document
                    CompanyDocument.objects.create(
                        company_code=company.company_code,
                        document_type=document_type[i],
                        document_number=document_number[i],
                        document_file=file,
                        issued_by=issued_by[i],
                        issued_date=issued_date[i],
                        expiry_date=expiry_date[i],
                        status=status[i],
                        remarks=remarks[i]
                    )


            return redirect('company_list')

        except Exception as e:
            print(f"Error updating company data: {str(e)}")
            return JsonResponse({"error": "Error updating company data."}, status=500)

    return redirect('company_list')


def check_company_code(request):
    company_code = request.GET.get('company_code')
    exists = CompanyMaster.objects.filter(company_code=company_code).exists()
    return JsonResponse({"exists": exists})



def company_delete(request):
    if request.method == "POST":
        comp_id=request.POST.get("company_id")

        if comp_id:
            company = get_object_or_404(CompanyMaster, company_id=comp_id)
            company.is_active = False  
            company.save()
            return redirect('company_list')
    return redirect('company_list')
        

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

        try:
            paycycle_master = PaycycleMaster.objects.get(comp_code=COMP_CODE, process_cycle=paycycle)
            vstart_date = paycycle_master.date_from  # Already a date object
            vend_date = paycycle_master.date_to  # Already a date object

            if excel_file:
                df = pd.read_excel(excel_file, engine='openpyxl')
                required_columns = ["S.No", "Emp Code", "Start Date", "End Date", "Project", "Attendance_type", "Morning", "Afternoon", "OT1", "OT2"]

                if all(column in df.columns for column in required_columns):
                    df['Error'] = ''  # Add a temporary column for error messages
                    error_data = []

                    for index, row in df.iterrows():
                        emp_code = row['Emp Code']
                        start_date = pd.to_datetime(row['Start Date']).date()  # Convert to date
                        end_date = pd.to_datetime(row['End Date']).date()  # Convert to date
                        project_code = row['Project']  # Get the project code from the row

                        # Validate Start Date and End Date
                        if not (vstart_date <= start_date <= vend_date and vstart_date <= end_date <= vend_date):
                            df.at[index, 'Error'] += f"Start Date and End Date must be within the paycycle range ({vstart_date} to {vend_date}). "

                        # Validate Employee Code
                        if not Employee.objects.filter(emp_code=emp_code, process_cycle=paycycle).exists():
                            df.at[index, 'Error'] += 'Invalid Emp Code for the selected paycycle. '

                        # Validate Project Code
                        if not projectMaster.objects.filter(prj_code=project_code).exists():
                            df.at[index, 'Error'] += 'Invalid Project Code. '

                        # Validate for null values
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
        except PaycycleMaster.DoesNotExist:
            messages.error(request, "Invalid paycycle.")
        except BadZipFile:
            messages.error(request, "The uploaded file is not a valid Excel file.")
        except Exception as e:
            messages.error(request, f"Error processing the file: {str(e)}")

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
                while (cur_date <= end_date):
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

        try:
            # Fetch paycycle data
            paycycle_data = PaycycleMaster.objects.filter(
                comp_code=COMP_CODE, process_cycle=paycycle, pay_process_month=paymonth, process_comp_flag=status
            ).first()

            if not paycycle_data:
                messages.error(request, "Invalid paycycle or paymonth.")
                return redirect('payroll_processing')

            # Fetch employee data using paycycle
            employee_data = Employee.objects.filter(process_cycle=paycycle, comp_code=COMP_CODE)
            print(employee_data)
            # Prepare payroll data
            payroll_data = []
            for employee in employee_data:
                # Fetch attendance data for the employee
                attendance_data = WorkerAttendanceRegister.objects.filter(
                    comp_code=COMP_CODE,
                    employee_code = employee.emp_code,
                    pay_cycle=paycycle,
                    pay_process_month=paymonth
                ).aggregate(
                    total_morning=Sum('morning'),
                    total_afternoon=Sum('afternoon'),
                    total_ot1=Sum('ot1'),
                    total_ot2=Sum('ot2')
                )
                total_morning = attendance_data.get('total_morning')
                total_afternoon = attendance_data.get('total_afternoon')

                # 🔥 Skip this employee if both morning and afternoon are None or 0
                if not total_morning and not total_afternoon:
                    continue  # Skip to next employee

                advance_data = AdvanceMaster.objects.filter(
                    comp_code=COMP_CODE,
                    emp_code=employee.emp_code,
                    is_active=True,
                    next_repayment_date__range=(paycycle_data.date_from, paycycle_data.date_to)
                )

                total_installment_amt = 0
                for advance in advance_data:
                    next_repayment_date = advance.next_repayment_date
                    if next_repayment_date and (paycycle_data.date_from <= next_repayment_date <= paycycle_data.date_to):
                        total_installment_amt += advance.instalment_amt

                # Calculate total working hours
                total_working_days = (attendance_data.get('total_morning', 0) + attendance_data.get('total_afternoon', 0)) / 8

                # Calculate basic and allowance per day
                basic_per_day = employee.basic_pay / paycycle_data.days_per_month if employee.basic_pay else 0
                allowance_per_day = employee.allowance / paycycle_data.days_per_month if employee.allowance else 0

                # Calculate total basic and allowance
                total_basic = basic_per_day * total_working_days
                total_allowance = allowance_per_day * total_working_days

                # Initialize earnings and deductions
                earn_amount = 0
                deduct_amount = 0

                # Fetch Earnings and Deductions Fixed
                earn_deduct_data = EarnDeductMaster.objects.filter(
                    comp_code=COMP_CODE,
                    employee_code=employee.emp_code,
                    is_active=True
                )

                for record in earn_deduct_data:
                    if record.earn_type == 'EARNINGS':
                        if record.prorated_flag:
                            earn_amount += (record.earn_deduct_amt / paycycle_data.days_per_month) * total_working_days
                        else:
                            earn_amount += record.earn_deduct_amt
                    elif record.earn_type == 'DEDUCTIONS':
                        if record.prorated_flag:
                            deduct_amount += (record.earn_deduct_amt / paycycle_data.days_per_month) * total_working_days
                        else:
                            deduct_amount += record.earn_deduct_amt

                # Fetch Adhoc Earnings and Deductions
                adhoc_earn_amount = 0
                adhoc_deduct_amount = 0

                adhoc_earn_deduct_data = PayrollEarnDeduct.objects.filter(
                    comp_code=COMP_CODE,
                    emp_code=employee.emp_code,
                    is_active=True,
                    pay_process_month=paymonth
                )

                for adhoc_record in adhoc_earn_deduct_data:
                    if adhoc_record.earn_deduct_type == 'EARNINGS':
                        adhoc_earn_amount += adhoc_record.pay_amount
                    else:
                        adhoc_deduct_amount += adhoc_record.pay_amount

                # Calculate OT1 and OT2 amounts
                ot1_hrs = attendance_data.get('total_ot1', 0)
                ot2_hrs = attendance_data.get('total_ot2', 0)
                basic_per_hour = basic_per_day / 8
                ot1_amt = (basic_per_hour * paycycle_data.ot1_amt) * ot1_hrs
                ot2_amt = (basic_per_hour * paycycle_data.ot2_amt) * ot2_hrs

                other_earnings = earn_amount + adhoc_earn_amount
                # Total Earnings and Deductions
                total_earnings = total_basic + total_allowance + earn_amount + adhoc_earn_amount + ot1_amt + ot2_amt
                total_deductions = deduct_amount + adhoc_deduct_amount + total_installment_amt

                # Calculate Net Pay
                net_pay =  total_earnings - total_deductions
                
                # Append data for HTML rendering
                payroll_data.append({
                    'employee_code': employee.emp_code,
                    'employee_name': employee.emp_name,
                    'Designation' : employee.designation,
                    'Basic': f"{employee.basic_pay:.2f}" if employee.basic_pay else "0.00",
                    'Allowance': f"{employee.allowance:.2f}" if employee.allowance else "0.00",
                    'basic_per_day': f"{basic_per_day:.2f}",
                    'basic_per_hour': f"{basic_per_hour:.2f}",
                    'allowance_per_day': f"{allowance_per_day:.2f}",
                    'total_basic': f"{total_basic:.2f}",
                    'total_allowance': f"{total_allowance:.2f}",
                    'earn_amount': f"{earn_amount:.2f}",
                    'deduct_amount': f"{deduct_amount:.2f}",
                    'adhoc_earn_amount': f"{adhoc_earn_amount:.2f}",
                    'adhoc_deduct_amount': f"{adhoc_deduct_amount:.2f}",
                    'total_earnings': f"{total_earnings:.2f}",
                    'total_deductions': f"{total_deductions:.2f}",
                    'ot1_amt': f"{ot1_amt:.2f}",
                    'ot2_amt': f"{ot2_amt:.2f}",
                    'installment_amt': f"{total_installment_amt:.2f}",
                    'net_pay': f"{net_pay:.2f}",
                    'paycycle': paycycle,
                    'paymonth': paymonth,
                    'total_days': paycycle_data.days_per_month,
                    'working_days': f"{total_working_days:.2f}",
                    'total_ot1': f"{ot1_hrs:.2f}",
                    'total_ot2': f"{ot2_hrs:.2f}",
                    'other_earnings': f"{other_earnings:.2f}"
                })

                # Delete existing records for the employee in the given pay cycle and month
                PayProcess.objects.filter(
                    comp_code=COMP_CODE,
                    pay_cycle=paycycle,
                    pay_month=paymonth,
                    employee_code=employee.emp_code
                ).delete()

                # Prepare new records for bulk insertion
                new_records = []

                # Insert net pay record
                new_records.append(PayProcess(
                    comp_code=COMP_CODE,
                    pay_cycle=paycycle,
                    pay_month=paymonth,
                    employee_code=employee.emp_code,
                    project_code=employee.department,
                    earn_type='NET',
                    earn_code='ER999',
                    morning=attendance_data.get('total_morning', 0),
                    afternoon=attendance_data.get('total_afternoon', 0),
                    ot1=ot1_hrs,
                    ot2=ot2_hrs,
                    amount=net_pay,
                    earn_reports='NET PAY'
                ))

                new_records.append(PayProcess(
                    comp_code=COMP_CODE,
                    pay_cycle=paycycle,
                    pay_month=paymonth,
                    employee_code=employee.emp_code,
                    project_code=employee.department,
                    earn_type='EARNINGS',
                    earn_code='ER001',
                    morning=attendance_data.get('total_morning', 0),
                    afternoon=attendance_data.get('total_afternoon', 0),
                    ot1=ot1_hrs,
                    ot2=ot2_hrs,
                    amount=total_basic,
                    earn_reports='EARN BASIC'
                ))

                new_records.append(PayProcess(
                    comp_code=COMP_CODE,
                    pay_cycle=paycycle,
                    pay_month=paymonth,
                    employee_code=employee.emp_code,
                    project_code=employee.department,
                    earn_type='EARNINGS',
                    earn_code='ER002',
                    morning=attendance_data.get('total_morning', 0),
                    afternoon=attendance_data.get('total_afternoon', 0),
                    ot1=ot1_hrs,
                    ot2=ot2_hrs,
                    amount=total_allowance,
                    earn_reports='EARN ALLOWANCE'
                ))

                new_records.append(PayProcess(
                    comp_code=COMP_CODE,
                    pay_cycle=paycycle,
                    pay_month=paymonth,
                    employee_code=employee.emp_code,
                    project_code=employee.department,
                    earn_type='EARNINGS',
                    earn_code='ER003',
                    # morning=attendance_data.get('total_morning', 0),
                    # afternoon=attendance_data.get('total_afternoon', 0),
                    ot1=ot1_hrs,
                    # ot2=ot2_hrs,
                    amount=ot1_amt,
                    earn_reports='EARN OT1'
                ))

                new_records.append(PayProcess(
                    comp_code=COMP_CODE,
                    pay_cycle=paycycle,
                    pay_month=paymonth,
                    employee_code=employee.emp_code,
                    project_code=employee.department,
                    earn_type='EARNINGS',
                    earn_code='ER004',
                    # morning=attendance_data.get('total_morning', 0),
                    # afternoon=attendance_data.get('total_afternoon', 0),
                    # ot1=ot1_hrs,
                    ot2=ot2_hrs,
                    amount=ot2_amt,
                    earn_reports='EARN OT2'
                ))

                # Insert additional earnings and deductions
                for record in earn_deduct_data:
                    new_records.append(PayProcess(
                        comp_code=COMP_CODE,
                        pay_cycle=paycycle,
                        pay_month=paymonth,
                        employee_code=employee.emp_code,
                        project_code=employee.department,
                        earn_type=record.earn_type,
                        earn_code=record.earn_deduct_code,
                        amount=record.earn_deduct_amt,
                        earn_reports=record.earn_deduct_code
                    ))

                # Insert adhoc earnings and deductions
                for adhoc_record in adhoc_earn_deduct_data:
                    new_records.append(PayProcess(
                        comp_code=COMP_CODE,
                        pay_cycle=paycycle,
                        pay_month=paymonth,
                        employee_code=employee.emp_code,
                        project_code=employee.department,
                        earn_type=adhoc_record.earn_deduct_type,
                        earn_code=adhoc_record.earn_deduct_code,
                        amount=adhoc_record.pay_amount,
                        earn_reports=adhoc_record.earn_deduct_code
                    ))

                for advance_record in advance_data:
                    new_records.append(PayProcess(
                        comp_code=COMP_CODE,
                        pay_cycle=paycycle,
                        pay_month=paymonth,
                        employee_code=employee.emp_code,
                        project_code=employee.department,
                        earn_type='DEDUCTIONS',
                        earn_code=advance_record.advance_code,
                        amount=advance_record.instalment_amt,
                        earn_reports='Advance Loan'
                    ))

                # Bulk insert new records
                PayProcess.objects.bulk_create(new_records)


            messages.success(request, "Payroll processed successfully.")
            return render(request, 'pages/payroll/payroll_processing/payroll_processing.html', {'payroll_data': payroll_data})
        except Exception as e:
            messages.error(request, f"Error processing payroll: {str(e)}")

        return redirect('payroll_processing')

    return render(request, 'pages/payroll/payroll_processing/payroll_processing.html', {'payroll_data': []})

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


def fetch_paymonth_adhoc(request):
    set_comp_code(request)  # Ensure this function is defined and works correctly
    paycycle = request.GET.get('paycycle')
    
    if paycycle:
        paymonths = PaycycleMaster.objects.filter(
            comp_code=COMP_CODE,
            process_cycle=paycycle
        ).values_list('pay_process_month', flat=True).distinct()
        
        employees = Employee.objects.filter(
            comp_code=COMP_CODE,
            process_cycle=paycycle
        ).values('emp_code', 'emp_name')  # Adjust fields as necessary
        
        # Prepare paymonth options
        options = '<option value="">-- Select Paymonth --</option>'
        for month in paymonths:
            options += f'<option value="{month}">{month}</option>'
        
        # Prepare employee options
        employee_options = '<option value="">-- Select Employee --</option>'
        for employee in employees:
            employee_options += f'<option value="{employee["emp_code"]}">{employee["emp_code"]} - {employee["emp_name"]}</option>'
        
        return JsonResponse({'options': options, 'employees': employee_options})
    
    return JsonResponse({'options': '<option value="">-- Select Paymonth --</option>', 'employees': '<option value="">-- Select Employee --</option>'})


def fetch_codes(request):
    set_comp_code(request)  # Make sure this function is defined
    type = request.GET.get('type')
    codes = []
    
    if type in ["EARNINGS", "DEDUCTION"]:
        
        codes = CodeMaster.objects.filter(
            base_type=type,
            comp_code=COMP_CODE,
            is_active='Y'
        ).values_list('base_value', 'base_description')
    return JsonResponse({
        'codes': list(codes),
        'status': 'success'
    })

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
        set_comp_code(request)
        keyword = request.GET.get('keyword', '').strip()
        page_number = request.GET.get('page', 1)
        get_url = request.get_full_path()

        # Adjust URL for pagination
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        # Initialize the query
        query = AdvanceMaster.objects.filter(comp_code=COMP_CODE)

        # Apply search filter if a keyword is provided
        if keyword:
            try:
                query = query.filter(
                    Q(emp_code__icontains=keyword) |
                    Q(advance_code__icontains=keyword) |
                    Q(advance_reference__icontains=keyword)
                )
            except Exception as e:
                print(f"Error in keyword search: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

        # Apply pagination
        paginator = Paginator(query.order_by('-reference_date'), PAGINATION_SIZE)

        try:
            advances_page = paginator.get_page(page_number)
        except PageNotAnInteger:
            advances_page = paginator.page(1)
        except EmptyPage:
            advances_page = paginator.page(paginator.num_pages)

        # Prepare the context for the template
        context = {
            'advances': advances_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': query.count()
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
            'comp_code': COMP_CODE,
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
            if (advance_id):  # If advance_id is provided, update the record
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


# Adhoc Earn Deduct

def adhoc_earn_deduct_list(request):
    set_comp_code(request)
    distinct_employees = PayrollEarnDeduct.objects.filter(comp_code=COMP_CODE).values(
        'emp_code', 'pay_process_month', 'pay_process_cycle'
    ).distinct()
    
    adhoc_groups = []
    for emp in distinct_employees:
        entries = PayrollEarnDeduct.objects.filter(
            comp_code=COMP_CODE,
            emp_code=emp['emp_code'],
            pay_process_month=emp['pay_process_month'],
            pay_process_cycle=emp['pay_process_cycle']
        )
        adhoc_groups.append({
            'emp_code': emp['emp_code'],
            'pay_process_month': emp['pay_process_month'],
            'pay_process_cycle': emp['pay_process_cycle'],
            'entries': entries
        })

    
    return render(request, 'pages/payroll/adhoc_earn_deduct/adhoc_earn_deduct.html', {'adhoc_groups': adhoc_groups})


def create_adhoc_earn_deduct(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            # Common fields
            pay_process_month = request.POST.get('pay_process_month', '')
            pay_process_cycle = request.POST.get('pay_process_cycle', '')
            emp_code = request.POST.get('emp_code', '')

            # Dynamic fields (multiple entries)
            earn_deduct_codes = request.POST.getlist('earn_deduct_code[]')
            earn_deduct_types = request.POST.getlist('earn_deduct_type[]')
            pay_amounts = request.POST.getlist('pay_amount[]')
            project_codes = request.POST.getlist('project_code[]')
            is_active_flags = request.POST.getlist('is_active[]')

            # Iterate through the dynamic fields and create records
            for i in range(len(earn_deduct_codes)):
                    PayrollEarnDeduct.objects.create(
                        comp_code=COMP_CODE,
                        emp_code=emp_code,
                        pay_process_month=pay_process_month,
                        pay_process_cycle=pay_process_cycle,
                        earn_deduct_code=earn_deduct_codes[i],
                        earn_deduct_type=earn_deduct_types[i],
                        pay_amount=pay_amounts[i],
                        project_code=project_codes[i] if project_codes[i] else None,
                        is_active=is_active_flags[i],
                        created_by=request.user.id if request.user.is_authenticated else 1
                    )

            # Redirect to the list page after successful creation
            return redirect('adhoc_earn_deduct_list')

        except Exception as e:
            # Handle errors and return a JSON response
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    # If not POST, return a bad request response
    return JsonResponse({'success': False, 'message': 'Invalid request method!'}, status=405)

def update_adhoc_earn_deduct(request, emp_code):
    set_comp_code(request)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method!'}, status=405)

    try:
        pay_process_month = request.POST.get('pay_process_month')
        pay_process_cycle = request.POST.get('pay_process_cycle')

        # Get lists from POST data
        earn_deduct_codes = request.POST.getlist('earn_deduct_code[]')
        earn_deduct_types = request.POST.getlist('earn_deduct_type[]')
        pay_amounts = request.POST.getlist('pay_amount[]')
        project_codes = request.POST.getlist('project_code[]')
        is_active_flags = request.POST.getlist('is_active[]')

        # Get all existing records for this employee/month/cycle
        existing_records = PayrollEarnDeduct.objects.filter(
            comp_code=COMP_CODE,
            emp_code=emp_code,
            pay_process_month=pay_process_month,
            pay_process_cycle=pay_process_cycle
        )

        # First delete all existing records (we'll recreate them with updated values)
        existing_records.delete()

        # Create new records with the updated values
        for i in range(len(earn_deduct_codes)):
            PayrollEarnDeduct.objects.create(
                comp_code=COMP_CODE,
                emp_code=emp_code,
                earn_deduct_code=earn_deduct_codes[i],
                earn_deduct_type=earn_deduct_types[i],
                pay_amount=pay_amounts[i],
                project_code=project_codes[i] if project_codes[i] else None,
                is_active=is_active_flags[i] == 'True',
                pay_process_month=pay_process_month,
                pay_process_cycle=pay_process_cycle,
                created_by=request.user.id if request.user.is_authenticated else 1,
                modified_by=request.user.id if request.user.is_authenticated else 1
            )

        return redirect('adhoc_earn_deduct_list')

    except Exception as e:
        print(f"Error updating records: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

def delete_adhoc_earn_deduct(request, emp_code):
    if request.method == 'POST':
        record = get_object_or_404(PayrollEarnDeduct, emp_code=emp_code)
        record.delete()
        return redirect('adhoc_earn_deduct_list')
    

def camp_list(request):
    set_comp_code(request)
    camps = CampMaster.objects.filter(comp_code=COMP_CODE, is_active=True)
    return render(request, 'pages/payroll/camp_master/camp_master.html', {'camps': camps})

def create_camp(request):
    set_comp_code(request)
    if request.method == 'POST':
        comp_code = COMP_CODE
        camp_code = request.POST.get('camp_code')
        camp_name = request.POST.get('camp_name')
        camp_agent = request.POST.get('camp_agent')
        
        # Convert empty date fields to None
        ejari_start_date = request.POST.get('ejari_start_date') or None
        ejari_end_date = request.POST.get('ejari_end_date') or None
        rental_contract_start_date = request.POST.get('rental_contract_start_date') or None
        rental_contract_end_date = request.POST.get('rental_contract_end_date') or None
        rental_agreement_start_date = request.POST.get('rental_agreement_start_date') or None
        rental_agreement_end_date = request.POST.get('rental_agreement_end_date') or None
        
        camp_value = request.POST.get('camp_value') or 0
        cheque_details = request.POST.get('cheque_details')

        upload_document = request.FILES.getlist('camp_doc[]')

        if upload_document:
            for file in upload_document:
                CampDocuments.objects.create(
                    comp_code=comp_code,
                    camp_code=camp_code,
                    document_name=file.name,
                    document_file=file
                )

        # Create CampMaster entry
        CampMaster.objects.create(
            comp_code=comp_code,
            camp_code=camp_code,
            camp_name=camp_name,
            camp_agent=camp_agent,
            ejari_start_date=ejari_start_date,
            ejari_end_date=ejari_end_date,
            rental_contract_start_date=rental_contract_start_date,
            rental_contract_end_date=rental_contract_end_date,
            rental_agreement_start_date=rental_agreement_start_date,
            rental_agreement_end_date=rental_agreement_end_date,
            camp_value=camp_value,
            cheque_details=cheque_details,
            created_by=1,
            is_active=True
        )

        # Camp Details
        block_name = request.POST.getlist('block_name[]')
        floor = request.POST.getlist('floor[]')
        type = request.POST.getlist('type[]')
        front_field = request.POST.getlist('front_field[]')
        no_of_rooms = request.POST.getlist('no_of_rooms[]')
        lower_bed_level = request.POST.getlist('lower_bed_level[]')
        upper_bed_level = request.POST.getlist('upper_bed_level[]')
        total_no_of_beds = request.POST.getlist('total_no_of_beds[]')
        occupied = request.POST.getlist('occupied[]')
        available = request.POST.getlist('available[]')

        for i in range(len(block_name)):
            CampDetails.objects.create(
                comp_code=comp_code,
                camp_code=camp_code,
                block=block_name[i],
                floor=floor[i],
                type=type[i],
                front_field=front_field[i],
                no_of_rooms=no_of_rooms[i] or 0,
                lower_bed=lower_bed_level[i] or 0,
                upper_bed=upper_bed_level[i] or 0,
                total_beds=total_no_of_beds[i] or 0,
                occupied_beds=occupied[i] or 0,
                available_beds=available[i] or 0,
            )

        # Cheque Details
        bank_name = request.POST.getlist('bank_name[]')
        cheque_no = request.POST.getlist('cheque_no[]')
        cheque_date = request.POST.getlist('cheque_date[]')
        cheque_amount = request.POST.getlist('cheque_amount[]')

        for i in range(len(bank_name)):
            CampCheque.objects.create(
                comp_code=comp_code,
                camp_code=camp_code,
                bank_name=bank_name[i],
                cheque_no=cheque_no[i] or None,  # Convert empty string to None
                cheque_date=cheque_date[i] or None,  # Convert empty string to None
                cheque_amount=cheque_amount[i] or 0,  # Default to 0 if empty
            )

        return redirect('camp_master')
    return render(request, 'pages/payroll/camp_master/camp_master.html')

@csrf_exempt
def camp_master_edit(request):
    set_comp_code(request)
    if request.method == 'GET':
        camp_id = request.GET.get('camp_id')
        try:
            camp_master = CampMaster.objects.get(camp_id=camp_id, comp_code = COMP_CODE)
            camp_details = CampDetails.objects.filter(comp_code=COMP_CODE, camp_code=camp_master.camp_code)
            camp_cheque = CampCheque.objects.filter(comp_code=COMP_CODE, camp_code=camp_master.camp_code)
            print(camp_master)
            
            camp_details_data = []

            for details in camp_details:
                camp_details_data.append({
                    'camp_details_id': details.camp_details_id,
                    'block_name': details.block,
                    'floor': details.floor,
                    'type': details.type,
                    'front_field': details.front_field,
                    'no_of_rooms': details.no_of_rooms,
                    'lower_bed_level': details.lower_bed,
                    'upper_bed_level': details.upper_bed,
                    'total_no_of_beds': details.total_beds,
                    'occupied': details.occupied_beds,
                    'available': details.available_beds
                })

            camp_cheque_data = []
            for cheque in camp_cheque:
                camp_cheque_data.append({
                    'camp_cheque_id': cheque.camp_cheque_id,
                    'bank_name': cheque.bank_name,
                    'cheque_no': cheque.cheque_no,
                    'cheque_date': cheque.cheque_date,
                    'cheque_amount': cheque.cheque_amount
                })
            
            return JsonResponse({
                "camp_id" : camp_master.camp_id,
                "camp_code" : camp_master.camp_code,
                "camp_name" : camp_master.camp_name,
                "camp_agent" : camp_master.camp_agent,
                "upload_document" : camp_master.upload_document.url if camp_master.upload_document else None,
                "ejari_start_date" : camp_master.ejari_start_date,
                "ejari_end_date" : camp_master.ejari_end_date,
                "rental_contract_start_date" : camp_master.rental_contract_start_date,
                "rental_contract_end_date" : camp_master.rental_contract_end_date,
                "rental_agreement_start_date" : camp_master.rental_agreement_start_date,
                "rental_agreement_end_date" : camp_master.rental_agreement_end_date,
                "camp_value" : camp_master.camp_value,
                "cheque_details" : camp_master.cheque_details,
                "camp_details": camp_details_data,
                "camp_cheque": camp_cheque_data
            })
        except CampMaster.DoesNotExist:
            return JsonResponse({"error": "Camp not found"}, status=404)
        except Exception as e:
            print(f"Error fetching camp details: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
        
    if request.method == "POST":
        camp_id = request.POST.get('camp_id')
        try:
            camp_master = CampMaster.objects.get(camp_id=camp_id)

            camp_master.camp_code = request.POST.get('camp_code')
            camp_master.camp_name = request.POST.get('camp_name')
            camp_master.camp_agent = request.POST.get('camp_agent')
            camp_master.ejari_start_date = request.POST.get('ejari_start_date') or None
            camp_master.ejari_end_date = request.POST.get('ejari_end_date') or None
            camp_master.rental_contract_start_date = request.POST.get('rental_contract_start_date') or None
            camp_master.rental_contract_end_date = request.POST.get('rental_contract_end_date') or None
            camp_master.rental_agreement_start_date = request.POST.get('rental_agreement_start_date') or None
            camp_master.rental_agreement_end_date = request.POST.get('rental_agreement_end_date') or None
            camp_master.camp_value = request.POST.get('camp_value')
            camp_master.cheque_details = request.POST.get('cheque_details')
            camp_master.modified_by = 1
            camp_master.save()

            upload_document = request.FILES.getlist('camp_doc[]')

            if upload_document:
                for file in upload_document:
                    CampDocuments.objects.create(
                        comp_code=camp_master.comp_code,
                        camp_code=camp_master.camp_code,
                        document_name=file.name,
                        document_file=file
                    )

            

            # Update Camp Details
            camp_detail_ids = request.POST.getlist('camp_detail_id[]')
            block_name = request.POST.getlist('block_name[]')
            floor = request.POST.getlist('floor[]')
            type = request.POST.getlist('type[]')
            front_field = request.POST.getlist('front_field[]')
            no_of_rooms = request.POST.getlist('no_of_rooms[]')
            lower_bed_level = request.POST.getlist('lower_bed_level[]')
            upper_bed_level = request.POST.getlist('upper_bed_level[]')
            total_no_of_beds = request.POST.getlist('total_no_of_beds[]')
            occupied = request.POST.getlist('occupied[]')
            available = request.POST.getlist('available[]')
            delete_camp_detail_ids = request.POST.getlist('delete_camp_detail_id[]')

            
            for cid, block, flr, typ, front, rooms, low, up, total, occ, avail, rmid in zip_longest(camp_detail_ids, block_name, floor, type, front_field, no_of_rooms,lower_bed_level, upper_bed_level, total_no_of_beds, occupied, available,delete_camp_detail_ids):
                if rmid:
                    camp_detail = CampDetails.objects.filter(camp_details_id=rmid)
                    camp_detail.delete()

                if cid:
                    camp_detail = CampDetails.objects.get(camp_details_id=cid)
                    camp_detail.block = block
                    camp_detail.floor = flr
                    camp_detail.type = typ
                    camp_detail.front_field = front
                    camp_detail.no_of_rooms = rooms or 0
                    camp_detail.lower_bed = low or 0
                    camp_detail.upper_bed = up or 0
                    camp_detail.total_beds = total or 0
                    camp_detail.occupied_beds = occ or 0
                    camp_detail.available_beds = avail or 0
                    camp_detail.save()
                elif not cid:
                        CampDetails.objects.create(
                            comp_code=COMP_CODE,
                            camp_code=camp_master.camp_code,
                            block=block,
                            floor=flr,
                            type=typ,
                            front_field=front,
                            no_of_rooms=rooms,
                            lower_bed=low,
                            upper_bed=up,
                            total_beds=total,
                            occupied_beds=occ,
                            available_beds=avail
                        )


            # Update Camp Cheque
            cheque_detail_ids = request.POST.getlist('cheque_detail_id[]')
            bank_name = request.POST.getlist('bank_name[]')
            cheque_no = request.POST.getlist('cheque_no[]')
            cheque_date = request.POST.getlist('cheque_date[]')
            cheque_amount = request.POST.getlist('cheque_amount[]')
            delete_cheque_detail_id = request.POST.getlist('delete_cheque_detail_id[]')

            for cid, bank, no, date, amount, rmid in zip_longest(cheque_detail_ids, bank_name, cheque_no, cheque_date, cheque_amount, delete_cheque_detail_id):
                print(cid, bank, no, date, amount, rmid)

                if rmid:
                    cheque = CampCheque.objects.filter(camp_cheque_id=rmid)
                    cheque.delete()
                
                if cid:
                    camp_cheque = CampCheque.objects.get(camp_cheque_id=cid)
                    camp_cheque.bank_name = bank
                    camp_cheque.cheque_no = no
                    camp_cheque.cheque_date = date or None
                    camp_cheque.cheque_amount = amount
                    camp_cheque.save()
                elif not cid:
                        CampCheque.objects.create(
                            comp_code=COMP_CODE,
                            camp_code=camp_master.camp_code,
                            bank_name=bank,
                            cheque_no=no,
                            cheque_date=date,
                            cheque_amount=amount
                        )

            return redirect('camp_master')
        except CampMaster.DoesNotExist:
            return JsonResponse({"error": "Camp not found"}, status=404)
        except Exception as e:
            print(f"Error updating camp details: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return redirect('camp_master')

def check_camp_code(request):
    camp_code = request.GET.get('camp_code', None)
    exists = CampMaster.objects.filter(camp_code=camp_code).exists()
    return JsonResponse({'exists': exists})

def get_camp_files(request, camp_code):
    try:
        # Define the folder path
        folder_path = os.path.join(settings.MEDIA_ROOT, 'camp_documents', camp_code)
        
        # Check if the folder exists
        if not os.path.exists(folder_path):
            return JsonResponse({'success': False, 'message': 'No files found for this camp code.'})
        
        # List all files in the folder
        files = os.listdir(folder_path)
        file_list = [
            {
                'file_name': file,
                'file_url': os.path.join(settings.MEDIA_URL, 'camp_documents', camp_code, file)
            }
            for file in files
        ]
        return JsonResponse({'success': True, 'files': file_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def camp_allocation(request):
    set_comp_code(request)

    # Get search keyword
    keyword = request.GET.get('keyword', '').strip()

    # Get page number for pagination
    page_number = request.GET.get('page', 1)

    # Filter camp allocations
    camp_allocations_query = CampAllocation.objects.filter(comp_code=COMP_CODE)
    if keyword:
        camp_allocations_query = camp_allocations_query.filter(
            Q(emp_code__icontains=keyword) |
            Q(current_camp_id__icontains=keyword) |
            Q(new_camp_id__icontains=keyword) |
            Q(reason__icontains=keyword)
        )

    # Paginate the results
    paginator = Paginator(camp_allocations_query.order_by('-camp_allocation_id'), 5)
    try:
        camp_allocations = paginator.get_page(page_number)
    except PageNotAnInteger:
        camp_allocations = paginator.page(1)
    except EmptyPage:
        camp_allocations = paginator.page(paginator.num_pages)

    # Build base URL for pagination
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    base_url = request.path + '?' + params.urlencode()

    # Fetch camps and employees
    camps = CampMaster.objects.filter(comp_code=COMP_CODE)
    employees = Employee.objects.filter(comp_code=COMP_CODE).values('emp_code', 'emp_name')

    return render(request, 'pages/payroll/camp_master/camp_transaction.html', {
        'camp_allocations': camp_allocations,
        'camps': camps,
        'employees': employees,
        'keyword': keyword,
        'base_url': base_url,  # Updated this line
    })


from django.db import transaction

@csrf_exempt
@transaction.atomic
def save_camp_allocations(request):
    try:
        # Get company code from session
        comp_code = request.session.get('comp_code', None)
        if not comp_code:
            return JsonResponse({'success': False, 'message': 'Company code not set'}, status=400)
        
        # Get raw POST data
        data = request.POST
        
        # Process each row of data
        employee_codes = data.getlist('employee_code[]')
        action_types = data.getlist('action_type[]')
        current_camps = data.getlist('current_camp[]')
        current_rooms = data.getlist('current_room[]')
        new_camps = data.getlist('new_camp[]')
        new_rooms = data.getlist('new_room[]')
        bed_numbers = data.getlist('bed_no[]')
        effective_dates = data.getlist('effective_date[]')
        reasons = data.getlist('reason[]')
        approvals = data.getlist('approval[]')
        
        print("Raw data received:")
        print(f"Employee codes: {employee_codes}")
        print(f"Action types: {action_types}")
        print(f"Current camps: {current_camps}")
        print(f"Current rooms: {current_rooms}")
        print(f"New camps: {new_camps}")
        print(f"New rooms: {new_rooms}")
        
        saved_count = 0
        
        print(len(employee_codes))
        # Process each transaction by index to ensure alignment
        for i in range(len(employee_codes)):
            print(new_camps)
            emp_code = employee_codes[i]
            action_type = action_types[i] if i < len(action_types) else ''
            current_camp = current_camps[i] if i < len(current_camps) else ''
            current_room = current_rooms[i] if i < len(current_rooms) else ''
            new_camp = new_camps[i] if i < len(new_camps) else ''
            new_room = new_rooms[i] if i < len(new_rooms) else ''
            bed_number = bed_numbers[i] if i < len(bed_numbers) else ''
            effective_date = effective_dates[i] if i < len(effective_dates) else None
            reason = reasons[i] if i < len(reasons) else ''
            approval = approvals[i] if i < len(approvals) else 'Pending'
            
            # Skip empty rows (where employee code is empty)
            if not emp_code:
                continue
                
            # Validate required fields
            if not action_type or not current_camp or not current_room:
                continue
                
            # Convert empty strings to None for optional fields
            new_camp = new_camp if new_camp else None
            new_room = new_room if new_room else None
            bed_number = bed_number if bed_number else None
            reason = reason if reason else None
            
            # Convert date string to date object
            effective_date_obj = None
            if effective_date:
                try:
                    effective_date_obj = datetime.strptime(effective_date, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    effective_date_obj = None
            
            print(f"\nProcessing row {i}:")
            print(f"Employee: {emp_code}")
            print(f"Action: {action_type}")
            print(f"Current Camp: {current_camp}")
            print(f"Current Room: {current_room}")
            print(f"New Camp: {new_camp}")
            print(f"New Room: {new_room}")
            
            # Create or update allocation record
            allocation, created = CampAllocation.objects.update_or_create(
                emp_code=emp_code,
                comp_code=comp_code,
                defaults={
                    'action_type': action_type,
                    'current_camp_id': current_camp,
                    'current_room_no': current_room,
                    'new_camp_id': new_camp,
                    'new_room_no': new_room,
                    'bed_number': bed_number,
                    'effective_date': effective_date_obj,
                    'reason': reason,
                    'approval_operation': approval,
                }
            )
            saved_count += 1
            print(f"Saved record for {emp_code} - {'Created' if created else 'Updated'}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully saved {saved_count} allocations',
            'redirect': '/camp_allocation/'  # Adjust as needed
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)