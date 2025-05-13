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
from django.db.models import F
from zipfile import BadZipFile
from security.models import UserRoleMapping, RoleMaster
from django.views import View
from .models import CodeMaster
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count
import pdb
from itertools import zip_longest
from django.db import connection
import urllib.parse
from datetime import date
import urllib.request
from io import BytesIO
from django.db import transaction
from django.utils import timezone
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import GratuitySettlement
from .models import EmployeePPDetails


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
    query = Employee.objects.filter(comp_code=COMP_CODE, staff_category__in=PAY_CYCLES)
    user = request.session.get("username")
    user_master = UserMaster.objects.filter(comp_code=COMP_CODE, is_active=True, user_id = user).values_list('view_emp_salary', flat=True)

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
            return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

    # Apply pagination
    paginator = Paginator(query.order_by('emp_code'), 6)

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
        employee.recruitment_details = EmployeeRecruitmentDetails.objects.filter(emp_code=employee.emp_code)

    # Prepare the context for the template
    context = {
        'employees': employees_page,
        'user_master': user_master,
        'current_url': current_url,
        'keyword': keyword,
        'result_cnt': query.count()
    }

    return render(request, 'pages/payroll/employee_master/employee_master.html', context)

from django.http import JsonResponse
from django.core import serializers
import json

def get_employee_details(request):
    set_comp_code(request)
    
    # Get employee_id from GET parameters
    employee_id = request.GET.get('employee_id')
    if not employee_id:
        return JsonResponse({'success': False, 'error': 'Employee ID is required'}, status=400)

    try:
        # Fetch the employee details
        employee = Employee.objects.get(employee_id=employee_id, comp_code=COMP_CODE)
        
        # Helper function to safely format dates
        def format_date(date_obj):
            return date_obj.strftime('%Y-%m-%d') if date_obj else None

        # Serialize the employee data
        employee_data = {
            'emp_code': employee.emp_code,
            'emp_name': employee.emp_name,
            'surname': employee.surname,
            'dob': format_date(employee.dob),
            'emp_sex': employee.emp_sex,
            'nationality': employee.nationality,
            'designation': employee.designation,
            'date_of_join': format_date(employee.date_of_join),
            'qualification': employee.qualification,
            'emp_status': employee.emp_status,
            'emp_sub_status': employee.emp_sub_status,
            'spouse_name': employee.spouse_name,
            'father_name': employee.father_name,
            'mother_name': employee.mother_name,
            'religion': employee.religion,
            'emp_marital_status': employee.emp_marital_status,
            'basic_pay': str(employee.basic_pay) if employee.basic_pay else None,  # Convert Decimal to string
            'allowance': str(employee.allowance) if employee.allowance else None,
            'department': employee.department,
            'process_cycle': employee.process_cycle,
            'local_addr_line1': employee.local_addr_line1,
            'local_addr_line2': employee.local_addr_line2,
            'local_city': employee.local_city,
            'local_state': employee.local_state,
            'local_country_code': employee.local_country_code,
            'local_phone_no': employee.local_phone_no,
            'res_addr_line1': employee.res_addr_line1,
            'res_addr_line2': employee.res_addr_line2,
            'res_city': employee.res_city,
            'res_state': employee.res_state,
            'res_country_code': employee.res_country_code,
            'res_phone_no': employee.res_phone_no,
            'visa_no': employee.visa_no,
            'visa_expiry': format_date(employee.visa_expiry),
            'emirates_no': employee.emirates_no,
            'emirate_expiry': format_date(employee.emirate_expiry),
            'passport_details': employee.passport_details,
            'passport_expiry': format_date(employee.passport_expiry_date),
        }

        # Fetch and serialize related data with error handling
        try:
            earn_deducts = list(EarnDeductMaster.objects.filter(
                comp_code=COMP_CODE, 
                employee_code=employee.emp_code
            ).values(
                'earn_type', 'earn_deduct_code', 'earn_deduct_amt', 'prorated_flag'
            ))
            # Convert Decimal to string for JSON serialization
            for item in earn_deducts:
                item['earn_deduct_amt'] = str(item['earn_deduct_amt']) if item['earn_deduct_amt'] is not None else None
        except Exception as e:
            earn_deducts = []

        try:
            documents = list(EmployeeDocument.objects.filter(
                emp_code=employee.emp_code, 
                relationship__isnull=True, 
                document_number__isnull=True
            ).values(
                'document_type', 'document_file'
            ))
        except Exception as e:
            documents = []

        try:
            dependents = list(EmployeeDocument.objects.filter(
                emp_code=employee.emp_code, 
                relationship__isnull=False
            ).values(
                'relationship', 'document_type', 'document_number', 
                'issued_date', 'expiry_date', 'document_file'
            ))
            # Format dates for dependents
            for dep in dependents:
                dep['issued_date'] = format_date(dep['issued_date'])
                dep['expiry_date'] = format_date(dep['expiry_date'])
        except Exception as e:
            dependents = []

        try:
            license_and_passes = list(EmployeeDocument.objects.filter(
                emp_code=employee.emp_code, 
                relationship__isnull=True, 
                issued_date__isnull=True
            ).values(
                'document_type', 'document_number', 'expiry_date', 'document_file'
            ))
            # Format dates for licenses
            for lic in license_and_passes:
                lic['expiry_date'] = format_date(lic['expiry_date'])
        except Exception as e:
            license_and_passes = []

        try:
            recruitment_details = list(EmployeeRecruitmentDetails.objects.filter(
                emp_code=employee.emp_code
            ).values(
                'agent_or_reference', 'location', 'change_status', 
                'recruitment_from', 'date'
            ))
            # Format dates for recruitment details
            for rec in recruitment_details:
                rec['date'] = format_date(rec['date'])
        except Exception as e:
            recruitment_details = []

        response_data = {
            'success': True,
            'data': {
                **employee_data,
                'earn_deducts': earn_deducts,
                'documents': documents,
                'dependents': dependents,
                'license_and_passes': license_and_passes,
                'recruitment_details': recruitment_details
            }
        }

        return JsonResponse(response_data)

    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
        
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
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'EMP'])
                    result = cursor.fetchone()
                    emp_code = result[0] if result else None
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
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
        employee.emp_status = request.POST.get("emp_status") if request.POST.get("emp_status") else 'ACTIVE'
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
        employee.sub_location = request.POST.get("sub_location")
        employee.designation = request.POST.get("designation")
        employee.department = request.POST.get("department")
        employee.date_of_join = request.POST.get("date_of_join") or None
        employee.date_of_rejoin = request.POST.get("date_of_rejoin") or None
        employee.depend_count = request.POST.get("depend_count") or None
        employee.staff_category = request.POST.get("staff_category")
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
        employee.change_status = request.FILES.get("change_status_file") or employee.change_status
        employee.visa_no = request.POST.get("visa_no")
        employee.emirates_no = request.POST.get("emirates_no")
        employee.visa_issued = request.POST.get("visa_issued") or None
        employee.visa_expiry = request.POST.get("visa_expiry") or None
        employee.visa_designation = request.POST.get("visa_designation")
        employee.visa_issued_emirate = request.POST.get("visa_issued_emirate")
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

        for doc_type, doc_number, doc_file, work_location, emirate_issued, expiry_date, category, comments in zip_longest(
                license_doc_types, license_doc_numbers, license_doc_files,
                license_work_locations, license_emirates_issued,
                license_expiry_dates, license_categories, license_comments):


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

        # Handle Recruitment Information
        recruitment_agents = request.POST.getlist("agent_name[]")
        recruitment_locations = request.POST.getlist("location[]")
        recruitment_change_statuses = request.POST.getlist("change_status[]")
        recruitment_froms = request.POST.getlist("recruitment_from[]")
        recruitment_dates = request.POST.getlist("recruitment_date[]")

        # Delete existing recruitment details for the employee
        # EmployeeRecruitmentDetails.objects.filter(comp_code=COMP_CODE, emp_code=emp_code).delete()

        # Save new recruitment details
        for agent, location, change_status, recruitment_from, date in zip(
                recruitment_agents, recruitment_locations, recruitment_change_statuses, recruitment_froms, recruitment_dates):
            if agent or location or change_status or recruitment_from or date:  # Ensure at least one field is filled
                EmployeeRecruitmentDetails.objects.create(
                    comp_code=COMP_CODE,
                    emp_code=emp_code,
                    agent_or_reference=agent,
                    location=location,
                    change_status=change_status,
                    recruitment_from=recruitment_from,
                    date=date if date else None
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
    total_employees = Employee.objects.filter(comp_code=COMP_CODE).count()
    active_employees = Employee.objects.filter(comp_code=COMP_CODE, emp_status='ACTIVE').count()
    on_leave_employees = Employee.objects.filter(comp_code=COMP_CODE, emp_status='ON_LEAVE').count()
    inactive_employees = Employee.objects.filter(comp_code=COMP_CODE, emp_status='INACTIVE').count()
    project_count = projectMaster.objects.filter(comp_code=COMP_CODE).count()
    holiday_count = HolidayMaster.objects.filter(comp_code=COMP_CODE).count()
    seed_count = SeedModel.objects.filter(comp_code=COMP_CODE).count()
    paycycle_count = PaycycleMaster.objects.filter(comp_code=COMP_CODE).count()
    company_count = CompanyMaster.objects.filter(company_code=COMP_CODE).count()
    grade_count = GradeMaster.objects.filter(comp_code=COMP_CODE).count()
    user_count = UserMaster.objects.filter(comp_code=COMP_CODE).count()
    camp_count = CampMaster.objects.filter(comp_code=COMP_CODE).count()

    # Prepare data for charts
    chart_data = {
        "labels": ["Employees", "Projects", "Holidays", "Seeds", "Paycycles", "Companies", "Grades", "Users", "Camps"],
        "values": [total_employees, project_count, holiday_count, seed_count, paycycle_count, company_count, grade_count, user_count, camp_count],
    }

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave_employees': on_leave_employees,
        'inactive_employees': inactive_employees,
        'project_count': project_count,
        'holiday_count': holiday_count,
        'seed_count': seed_count,
        'paycycle_count': paycycle_count,
        'company_count': company_count,
        'grade_count': grade_count,
        'user_count': user_count,
        'camp_count': camp_count,
        'chart_data': chart_data,
    }
    
    return render(request, 'pages/dashboard/index.html', context)

def my_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        selected_company = request.POST.get("selected_company")

        try:
            user = UserMaster.objects.get(user_id=username, is_active=True)

            if password == user.password:
                request.session["username"] = user.user_id

                get_companies = user.company.split(':') if user.company else []
                if len(get_companies) > 1:
                    if not selected_company:
                        messages.error(request, "Please select a company.")
                        return render(request, "auth/login.html")
                    request.session["comp_code"] = selected_company
                else:
                    request.session["comp_code"] = user.comp_code

                request.session["user_paycycles"] = user.user_paycycles

                company = CompanyMaster.objects.get(company_code=request.session["comp_code"])
                request.session["image_url"] = str(company.image_url) if company.image_url else None

                # Fetch role ID from UserRoleMapping
                user_role_mapping = UserRoleMapping.objects.get(userid=user.user_master_id, is_active=True)
                role_id = user_role_mapping.roleid

                # Fetch role name from RoleMaster
                role = RoleMaster.objects.get(id=role_id)
                request.session["role"] = role.role_name
                request.session["role_id"] = role_id

                set_comp_code(request)
                
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

@csrf_exempt
def check_user_companies(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            user = UserMaster.objects.get(user_id=username, is_active=True)
            companies = user.company.split(':')
            
            return JsonResponse({
                'success': True,
                'companies': companies
            })
        except UserMaster.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

def dashboard_view(request):
    set_comp_code(request)
    try:
        role_id = request.session.get("role_id")
        permission_data = list(RoleMenu.objects.filter(role_id=role_id, is_active=True).values('menu_id', 'view', 'add', 'edit', 'delete'))
        menu_ids = RoleMenu.objects.filter(role_id=role_id, view=True).values_list('menu_id', flat=True)
        parent_menu_data = list(Menu.objects.filter(menu_id__in=menu_ids, parent_menu_id='No Parent', comp_code=COMP_CODE).order_by('display_order').values('menu_id', 'screen_name'))
        child_menu_data = list(Menu.objects.filter(menu_id__in=menu_ids, comp_code=COMP_CODE).exclude(parent_menu_id='No Parent').order_by('display_order').values('menu_id', 'screen_name', 'url', 'parent_menu_id'))
        response_data = {'status': 'success', 'parent_menu_data': parent_menu_data, 'child_menu_data': child_menu_data, 'permission_data': permission_data}
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
    if request.method == 'POST':
        try:
            # Check if it's an Excel upload
            if 'excel_file' in request.FILES:
                excel_file = request.FILES['excel_file']
                if not excel_file.name.endswith(('.xlsx', '.xls')):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please upload a valid Excel file (.xlsx or .xls)'
                    })

                # Read Excel file
                df = pd.read_excel(excel_file)
                
                # Validate required columns
                required_columns = [
                    'Project Code*', 'Project Name*', 'Project Description*',
                    'Project Type*', 'Project Value*', 'Start Date* (YYYY-MM-DD)',
                    'End Date* (YYYY-MM-DD)'
                ]
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Missing required columns: {", ".join(missing_columns)}'
                    })

                # Process each row
                valid_records = []
                invalid_records = []
                
                for index, row in df.iterrows():
                    try:
                        missing_fields = [col for col in required_columns if pd.isna(row[col])]
                        if missing_fields:
                            invalid_records.append({
                                'row': index + 2,
                                'error': f'Missing required fields: {", ".join(missing_fields)}'
                            })
                            continue


                        # Validate dates
                        try:
                            start_date = pd.to_datetime(row['Start Date* (YYYY-MM-DD)']).date()
                            end_date = pd.to_datetime(row['End Date* (YYYY-MM-DD)']).date()
                        except:
                            invalid_records.append({
                                'row': index + 2,
                                'error': 'Invalid date format'
                            })
                            continue

                        # Validate project code
                        if projectMaster.objects.filter(prj_code=row['Project Code*']).exists():
                            invalid_records.append({
                                'row': index + 2,
                                'error': 'Project code already exists'
                            })
                            continue

                        # Add to valid records
                        valid_records.append({
                            'row': index + 2,
                            'project_code': row['Project Code*'],
                            'project_name': row['Project Name*'],
                            'project_type': row['Project Type*'],
                            'start_date': start_date.strftime('%Y-%m-%d'),
                            'end_date': end_date.strftime('%Y-%m-%d'),
                            'project_value': row['Project Value*']
                        })

                    except Exception as e:
                        invalid_records.append({
                            'row': index + 2,
                            'error': str(e)
                        })

                # If this is just a preview request
                if request.POST.get('preview') == 'true':
                    return JsonResponse({
                        'status': 'preview',
                        'total_records': len(df),
                        'valid_records': valid_records,
                        'invalid_records': invalid_records
                    })

                # If this is the final upload
                if request.POST.get('confirm_upload') == 'true':
                    success_count = 0
                    for record in valid_records:
                        try:
                            # Get the original row data
                            row_data = df.iloc[record['row'] - 2]
                            
                            # Create project
                            project = projectMaster(
                                comp_code=request.session.get('comp_code'),
                                prj_code=row_data['Project Code*'],
                                prj_name=row_data['Project Name*'],
                                project_description=row_data['Project Description*'],
                                project_type=row_data['Project Type*'],
                                project_value=row_data['Project Value*'],
                                timeline_from=pd.to_datetime(row_data['Start Date* (YYYY-MM-DD)']).date(),
                                timeline_to=pd.to_datetime(row_data['End Date* (YYYY-MM-DD)']).date(),
                                prj_city=row_data.get('Project City', ''),
                                service_type=row_data.get('Service Type', ''),
                                service_category=row_data.get('Service Category', ''),
                                pro_sub_location=row_data.get('Project Sub Location', ''),
                                customer=row_data.get('Customer Code', ''),
                                agreement_ref=row_data.get('Agreement Ref', ''),
                                op_head=row_data.get('OP Head Code', ''),
                                manager=row_data.get('Manager Code', ''),
                                commercial_manager=row_data.get('Commercial Manager Code', ''),
                                project_engineer=row_data.get('Project Engineer Code', ''),
                                project_supervisor=row_data.get('Project Supervisor Code', ''),
                                procurement_user=row_data.get('Procurement User Code', ''),
                                indent_user=row_data.get('Indent User Code', ''),
                                final_contract_value=row_data.get('Final Contract Value', 0),
                                project_status=row_data.get('Project Status', ''),
                                created_by=1
                            )
                            project.save()
                            success_count += 1
                        except Exception as e:
                            invalid_records.append({
                                'row': record['row'],
                                'error': f'Error saving record: {str(e)}'
                            })

                    return JsonResponse({
                        'status': 'success',
                        'message': f'Successfully imported {success_count} projects'
                    })

            # Handle regular form submission
            else:
                # Your existing form handling code here
                pass

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
        
    # GET request handling
    # Your existing GET request code here
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
                    "op_head": project.op_head.split(':') if project.op_head else [],
                    "manager": project.manager.split(':') if project.manager else [],
                    "commercial_manager": project.commercial_manager.split(':') if project.commercial_manager else [],
                    "project_engineer": project.project_engineer.split(':') if project.project_engineer else [],
                    "project_supervisor": project.project_supervisor.split(':') if project.project_supervisor else [], 
                    "procurement_user": project.procurement_user.split(':') if project.procurement_user else [],
                    "indent_user": project.indent_user.split(':') if project.indent_user else [],
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
                    "project_engineer": project.project_engineer,
                    "project_supervisor": project.project_supervisor,
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

            # Render the template
            return render(request, template_name, context)
       
    if request.method == "POST":
        project_id = request.POST.get("project_id")

        # Get prj_city from the POST request
        prj_city = request.POST.getlist('prj_city')  # Get list of selected cities
        prj_city_str = ':'.join(prj_city)  # Convert list to colon-separated string

        pro_sub_location = request.POST.getlist('pro_sub_location')  # Get list of selected sub-locations
        prj_sub_location_str = ':'.join(pro_sub_location)  # Convert list to colon-separated string

        # Handle multi-select fields
        op_heads = request.POST.getlist("op_head")  # Get list of selected OP Heads
        managers = request.POST.getlist("manager")  # Get list of selected Managers
        commercial_managers = request.POST.getlist("commercial_manager")  # Get list of selected Commercial Managers
        project_engineers = request.POST.getlist("project_engineer")  # Get list of selected Project Engineers
        project_supervisors = request.POST.getlist("project_supervisor")  # Get list of selected Project Supervisors
        procurement_users = request.POST.getlist("procurement_user")  # Get list of selected Procurement Users
        indent_users = request.POST.getlist("indent_user")  # Get list of selected Indent Users

        # Convert lists to colon-separated strings for storage
        op_heads_str = ":".join(op_heads)
        managers_str = ":".join(managers)
        commercial_managers_str = ":".join(commercial_managers)
        project_engineers_str = ":".join(project_engineers)
        project_supervisors_str = ":".join(project_supervisors)
        procurement_users_str = ":".join(procurement_users)
        indent_users_str = ":".join(indent_users)

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
            project.pro_sub_location = prj_sub_location_str
            project.op_head = op_heads_str
            project.manager = managers_str
            project.commercial_manager = commercial_managers_str
            project.project_engineer = project_engineers_str
            project.project_supervisor = project_supervisors_str
            project.procurement_user = procurement_users_str
            project.indent_user = indent_users_str
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
                op_head=op_heads_str,
                manager=managers_str,
                commercial_manager=commercial_managers_str,
                project_engineer=project_engineers_str,
                project_supervisor=project_supervisors_str,
                procurement_user=procurement_users,
                indent_user=indent_users,
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

def get_project_locations(request):
    project_code = request.GET.get('project_code')
    if project_code:
        # Fetch locations for the selected project
        locations = projectMaster.objects.filter(project_code=project_code).values('code', 'name')  # Adjust fields as needed
        return JsonResponse({'success': True, 'locations': list(locations)})
    return JsonResponse({'success': False, 'message': 'Invalid project code.'})

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
        set_comp_code(request)
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

            user_company = request.POST.getlist('company')
            user_company_str = ':'.join(user_company)

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
                user_paycycles=user_paycycles_str,  # Save as colon-separated string
                view_emp_salary=request.POST.get('view_emp_salary'),
                company=user_company_str
            )

            user.full_clean()
            user.save()
            return JsonResponse({'status': 'success', 'redirect_url': reverse('user_list')})

        except Exception as e:
            return JsonResponse({'status': 'error', 'field': 'general', 'message': str(e)})

class UserMasterUpdate(View):
    def post(self, request, user_master_id):
        set_comp_code(request)
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
            user_company = request.POST.getlist('company')
            user.company = ':'.join(user_company)
            user_paycycles = request.POST.getlist('user_paycycles')  # Get list of selected paycycles
            user.user_paycycles = ':'.join(user_paycycles)  # Convert list to colon-separated string
            
            user.is_active = request.POST.get('is_active') == 'on'
            user.view_emp_salary = request.POST.get('view_emp_salary')
            user.full_clean()
            user.save()

            return JsonResponse({'status': 'success', 'redirect_url': reverse('user_list')})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
class UserMasterDelete(View):
    def post(self, request, user_master_id):
        set_comp_code(request)
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
            pass

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

        # Get search keyword
        keyword = request.GET.get('keyword', '')
        
        # Base query
        menus = Menu.objects.filter(comp_code=COMP_CODE).order_by('display_order')
        
        # Apply search filter if keyword exists
        if keyword:
            menus = menus.filter(
                Q(menu_name__icontains=keyword) |
                Q(screen_name__icontains=keyword) |
                Q(url__icontains=keyword)
            )
        
        # Get total count for pagination
        result_cnt = menus.count()
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(menus, PAGINATION_SIZE)  # Show 10 items per page
        
        try:
            menus = paginator.page(page)
        except PageNotAnInteger:
            menus = paginator.page(1)
        except EmptyPage:
            menus = paginator.page(paginator.num_pages)
        
        fetch_details = Menu.objects.filter(comp_code=COMP_CODE, parent_menu_id="No Parent")
        context = {
            'menus': menus,
            'result_cnt': result_cnt,
            'keyword': keyword,
            'current_url': request.path,
            'fetch_details': fetch_details
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

            return JsonResponse({'success': True})
        except Exception as e:
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
                'is_edit_checked': role_menu.edit if role_menu else False,
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
            return JsonResponse({"error": "Company data not found."}, status=404)
        
    if request.method == "POST":
        comp_id = request.POST.get('company_id')
        try:
            company = get_object_or_404(CompanyMaster, company_id=int(comp_id))    

            company.image_url = request.FILES.get("image_url") or company.image_url
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
                        pass

                if doc_id and doc_id != "" and doc_id != "undefined":  # Update existing document
                    try:
                        doc = CompanyDocument.objects.get(company_id=doc_id, company_code=company.company_code)
                        doc.document_type = document_type[i]
                        doc.document_number = document_number[i]
                        doc.issued_by = issued_by[i]
                        doc.issued_date = issued_date[i] or None
                        doc.expiry_date = expiry_date[i] or None
                        doc.status = status[i]
                        doc.remarks = remarks[i]
                        if file:
                            doc.document_file = file
                        doc.save()
                    except CompanyDocument.DoesNotExist:
                        pass
                else:  # New document
                    CompanyDocument.objects.create(
                        company_code=company.company_code,
                        document_type=document_type[i],
                        document_number=document_number[i],
                        document_file=file,
                        issued_by=issued_by[i],
                        issued_date=issued_date[i] or None,
                        expiry_date=expiry_date[i] or None,
                        status=status[i],
                        remarks=remarks[i]
                    )


            return redirect('company_list')

        except Exception as e:
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
                    project_code=employee.prj_code,
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
                    project_code=employee.prj_code,
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
                    project_code=employee.prj_code,
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
                    project_code=employee.prj_code,
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
                        project_code=employee.prj_code,
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
                        project_code=employee.prj_code,
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
                        project_code=employee.prj_code,
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
            query = query.filter(
                Q(emp_code__icontains=keyword) |
                Q(advance_code__icontains=keyword) |
                Q(advance_reference__icontains=keyword)
            )

        # Fetch employee names and add them to the query
        advances_with_details = []
        for advance in query:
            emp_name = Employee.objects.filter(emp_code=advance.emp_code).values_list('emp_name', flat=True).first()
            advances_with_details.append({
                'emp_code': advance.emp_code,
                'emp_name': emp_name or 'N/A',  # Default to 'N/A' if no employee name is found
                'advance_code': advance.advance_code,
                'repayment_from': advance.repayment_from,
                'next_repayment_date': advance.next_repayment_date,
                'is_active': advance.is_active,
                'advance_id': advance.advance_id
            })

        # Apply pagination
        paginator = Paginator(advances_with_details, PAGINATION_SIZE)

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
            'reference_date': advance.reference_date,
            'total_amt': advance.total_amt,
            'instalment_amt': advance.instalment_amt,
            'paid_amt': advance.paid_amt,
            'total_no_instalment': advance.total_no_instalment,
            'balance_no_instalment': advance.balance_no_instalment,
            'repayment_from': advance.repayment_from,
            'next_repayment_date': advance.next_repayment_date,
            'default_count': advance.default_count,
            'waiver_amt': advance.waiver_amt,
            'waiver_date': advance.waiver_date,
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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

def adhoc_earn_deduct_list(request):
    set_comp_code(request)
    keyword = request.GET.get('keyword', '').strip()  # Get the search keyword
    page_number = request.GET.get('page', 1)  # Get the current page number

    # Filter distinct employees based on the keyword
    distinct_employees = PayrollEarnDeduct.objects.filter(comp_code=COMP_CODE).values(
        'emp_code', 'pay_process_month', 'pay_process_cycle', 'earn_deduct_type'
    ).distinct()

    if keyword:
        distinct_employees = distinct_employees.filter(
            Q(emp_code__icontains=keyword) |
            Q(pay_process_month__icontains=keyword) |
            Q(pay_process_cycle__icontains=keyword)
        )

    adhoc_groups = []
    for emp in distinct_employees:
        # Fetch employee name from the Employee model
        emp_name = Employee.objects.filter(emp_code=emp['emp_code']).values_list('emp_name', flat=True).first()

        entries = PayrollEarnDeduct.objects.filter(
            comp_code=COMP_CODE,
            emp_code=emp['emp_code'],
            pay_process_month=emp['pay_process_month'],
            pay_process_cycle=emp['pay_process_cycle']
        )
        adhoc_groups.append({
            'emp_code': emp['emp_code'],
            'emp_name': emp_name,  # Include employee name
            'pay_process_month': emp['pay_process_month'],
            'pay_process_cycle': emp['pay_process_cycle'],
            'earn_deduct_type': emp['earn_deduct_type'],
            'entries': entries
        })

    # Paginate the results
    paginator = Paginator(adhoc_groups, PAGINATION_SIZE)
    try:
        adhoc_groups_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        adhoc_groups_page = paginator.page(1)
    except EmptyPage:
        adhoc_groups_page = paginator.page(paginator.num_pages)

    return render(request, 'pages/payroll/adhoc_earn_deduct/adhoc_earn_deduct.html', {
        'adhoc_groups': adhoc_groups_page,
        'keyword': keyword,
    })


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
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

def delete_adhoc_earn_deduct(request, emp_code):
    if request.method == 'POST':
        record = get_object_or_404(PayrollEarnDeduct, emp_code=emp_code)
        record.delete()
        return redirect('adhoc_earn_deduct_list')
    

def camp_list(request):
    set_comp_code(request)
    
    # Get search keyword
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)
    
    # Get the current URL for pagination links
    get_url = request.get_full_path()
    
    # Adjust URL for pagination
    if '?keyword' in get_url:
        get_url = get_url.split('&page=')[0]
        current_url = f"{get_url}&"
    else:
        get_url = get_url.split('?')[0]
        current_url = f"{get_url}?"
    
    # Initialize the query
    camps_query = CampMaster.objects.filter(comp_code=COMP_CODE, is_active=True)
    
    # Apply search filter if keyword is provided
    if keyword:
        camps_query = camps_query.filter(
            Q(camp_code__icontains=keyword) |
            Q(camp_name__icontains=keyword) |
            Q(camp_agent__icontains=keyword)
        )
    
    # Apply pagination
    paginator = Paginator(camps_query.order_by('camp_code'), PAGINATION_SIZE)  # Adjust PAGINATION_SIZE as needed
    
    try:
        camps = paginator.get_page(page_number)
    except PageNotAnInteger:
        camps = paginator.page(1)
    except EmptyPage:
        camps = paginator.page(paginator.num_pages)
    
    context = {
        'camps': camps,
        'current_url': current_url,
        'keyword': keyword,
        'result_cnt': camps_query.count()
    }
    
    return render(request, 'pages/payroll/camp_master/camp_master.html', context)

def create_camp(request):
    set_comp_code(request)
    if request.method == 'POST':
        
        
        comp_code = COMP_CODE
        # camp_code = request.POST.get('camp_code')
        camp_name = request.POST.get('camp_name')
        camp_agent = request.POST.get('camp_agent')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'CAMP'])
                result = cursor.fetchone()
                camp_code = result[0] if result else None
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

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
        room_type = request.POST.getlist('type[]')
        room_no = request.POST.getlist('room_no[]')
        as_per_mohre = request.POST.getlist('as_per_mohre[]')
        allocated = request.POST.getlist('allocated[]')
        as_per_rental = request.POST.getlist('as_per_rental[]')
        allocation_building = request.POST.getlist('allocation_building[]')
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
                type=room_type[i],
                room_no=room_no[i] or 0,
                as_per_mohre=as_per_mohre[i] or 0,
                allocated=allocated[i] or 0,
                as_per_rental=as_per_rental[i] or 0,
                allocation_building=allocation_building[i],
                lower_bed=lower_bed_level[i] or 0,
                upper_bed=upper_bed_level[i] or 0,
                total_beds=total_no_of_beds[i] or 0,
                occupied_beds=occupied[i] or 0,
                available_beds=available[i] or 0,
            )

        # Generate and insert bed data into CampBeds
            lower_beds = int(lower_bed_level[i]) if lower_bed_level[i] else 0
            upper_beds = int(upper_bed_level[i]) if upper_bed_level[i] else 0

            for j in range(1, lower_beds + 1):
                CampBeds.objects.create(
                    comp_code=comp_code,
                    camp_code=camp_code,
                    block=block_name[i],
                    room_no=room_no[i],
                    bed_no=f"L-{j}",
                    bed_status="N",
                    floor = floor[i]
                )

            for j in range(1, upper_beds + 1):
                CampBeds.objects.create(
                    comp_code=comp_code,
                    camp_code=camp_code,
                    block=block_name[i],
                    room_no=room_no[i],
                    bed_no=f"U-{j}",
                    bed_status="N",
                    floor = floor[i]
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
            camp_documents = CampDocuments.objects.filter(comp_code=COMP_CODE, camp_code=camp_master.camp_code)
            
            camp_details_data = []

            for details in camp_details:
                camp_details_data.append({
                    'camp_details_id': details.camp_details_id,
                    'block': details.block,
                    'floor': details.floor,
                    'type': details.type,
                    'room_no': details.room_no,
                    'as_per_mohre': details.as_per_mohre,
                    'allocated': details.allocated,
                    'as_per_rental': details.as_per_rental,
                    'allocation_building': details.allocation_building,
                    'lower_bed': details.lower_bed,
                    'upper_bed': details.upper_bed,
                    'total_beds': details.total_beds,
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

            camp_documents_data = []
            for document in camp_documents:
                camp_documents_data.append({
                    'camp_document_id': document.camp_document_id,
                    'document_name': document.document_name,
                    'document_url': document.document_file.url if document.document_file else None
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
                "camp_cheque": camp_cheque_data,
                "camp_documents": camp_documents_data
            })
        except CampMaster.DoesNotExist:
            return JsonResponse({"error": "Camp not found"}, status=404)
        except Exception as e:
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
            room_no = request.POST.getlist('room_no[]')
            as_per_mohre = request.POST.getlist('as_per_mohre[]')
            allocated = request.POST.getlist('allocated[]')
            as_per_rental = request.POST.getlist('as_per_rental[]')
            allocation_building = request.POST.getlist('allocation_building[]')
            lower_bed_level = request.POST.getlist('lower_bed_level[]')
            upper_bed_level = request.POST.getlist('upper_bed_level[]')
            total_no_of_beds = request.POST.getlist('total_no_of_beds[]')
            occupied = request.POST.getlist('occupied[]')
            available = request.POST.getlist('available[]')
            delete_camp_detail_ids = request.POST.getlist('delete_camp_detail_id[]') 
            
            for cid, block, flr, typ, rooms, apm, alloc, apr, ab, low, up, total, occ, avail, rmid in zip_longest(
                camp_detail_ids, block_name, floor, type, room_no, as_per_mohre, allocated, as_per_rental,
                allocation_building, lower_bed_level, upper_bed_level, total_no_of_beds, occupied, available, delete_camp_detail_ids
            ):
                if rmid:
                    camp_detail = CampDetails.objects.filter(camp_details_id=rmid)

                if cid:
                    camp_detail = CampDetails.objects.get(camp_details_id=cid)
                    camp_detail.block = block
                    camp_detail.floor = flr
                    camp_detail.type = typ
                    camp_detail.room_no = rooms or 0
                    camp_detail.as_per_mohre = apm or 0
                    camp_detail.allocated = alloc or 0
                    camp_detail.as_per_rental = apr or 0
                    camp_detail.allocation_building = ab
                    camp_detail.lower_bed = low or 0
                    camp_detail.upper_bed = up or 0
                    camp_detail.total_beds = total or 0
                    camp_detail.occupied_beds = occ or 0
                    camp_detail.available_beds = avail or 0
                    camp_detail.save()
                    # Update CampBeds for the updated CampDetails
                    # CampBeds.objects.filter(camp_code=camp_master.camp_code, block=block, room_no=rooms).delete()
                    # lower_beds = int(low) if low else 0
                    # upper_beds = int(up) if up else 0

                    # for j in range(1, lower_beds + 1):
                    #     CampBeds.objects.create(
                    #         comp_code=COMP_CODE,
                    #         camp_code=camp_master.camp_code,
                    #         block=block,
                    #         room_no=rooms,
                    #         bed_no=f"L-{j}",
                    #         bed_status="N"
                    #     )

                    # for j in range(1, upper_beds + 1):
                    #     CampBeds.objects.create(
                    #         comp_code=COMP_CODE,
                    #         camp_code=camp_master.camp_code,
                    #         block=block,
                    #         room_no=rooms,
                    #         bed_no=f"U-{j}",
                    #         bed_status="N"
                    #     )
                elif not cid and not rmid:
                        if block and flr and typ:
                            CampDetails.objects.create(
                                comp_code=COMP_CODE,
                                camp_code=camp_master.camp_code,
                                block=block,
                                floor=flr,
                                type=typ,
                                room_no=rooms,
                                as_per_mohre=apm or 0,
                                allocated=alloc or 0,
                                as_per_rental=apr or 0,
                                lower_bed=low,
                                upper_bed=up,
                                total_beds=total,
                                occupied_beds=occ or 0,
                                available_beds=avail or 0
                            )
                            # Create CampBeds for the new CampDetails
                            lower_beds = int(low) if low else 0
                            upper_beds = int(up) if up else 0
                            for j in range(1, lower_beds + 1):
                                CampBeds.objects.create(
                                    comp_code=COMP_CODE,
                                    camp_code=camp_master.camp_code,
                                    block=block,
                                    room_no=rooms,
                                    bed_no=f"L-{j}",
                                    bed_status="N",
                                    floor = flr
                                )

                            for j in range(1, upper_beds + 1):
                                CampBeds.objects.create(
                                    comp_code=COMP_CODE,
                                    camp_code=camp_master.camp_code,
                                    block=block,
                                    room_no=rooms,
                                    bed_no=f"U-{j}",
                                    bed_status="N",
                                    floor = flr
                                )


            # Update Camp Cheque
            cheque_detail_ids = request.POST.getlist('cheque_detail_id[]')
            bank_name = request.POST.getlist('bank_name[]')
            cheque_no = request.POST.getlist('cheque_no[]')
            cheque_date = request.POST.getlist('cheque_date[]')
            cheque_amount = request.POST.getlist('cheque_amount[]')
            delete_cheque_detail_id = request.POST.getlist('delete_cheque_detail_id[]')

            for cid, bank, no, date, amount, rmid in zip_longest(cheque_detail_ids, bank_name, cheque_no, cheque_date, cheque_amount, delete_cheque_detail_id):

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
            return JsonResponse({"error": str(e)}, status=500)
    return redirect('camp_master')

def check_camp_code(request):
    camp_code = request.GET.get('camp_code', None)
    exists = CampMaster.objects.filter(camp_code=camp_code).exists()
    return JsonResponse({'exists': exists})

def camp_allocation_list(request):
    set_comp_code(request)
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)

    # Filter transactions based on keyword
    transactions = CampAllocation.objects.filter(comp_code=COMP_CODE)
    if keyword:
        transactions = transactions.filter(
            Q(employee_code__icontains=keyword) |
            Q(employee_name__icontains=keyword) |
            Q(camp__icontains=keyword)
        )

    # Paginate the results
    paginator = Paginator(transactions.order_by('-created_on'), PAGINATION_SIZE)
    try:
        transactions_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    return render(request, 'pages/payroll/camp_master/camp_transaction.html', {
        'camp_transactions': transactions_page,
        'keyword': keyword,
    })

def check_employee_allocation(request):
    employee_code = request.GET.get('employee_code')
    if employee_code:
        is_allocated = CampAllocation.objects.filter(emp_code=employee_code, operational_approval = 'Yes').exists()
        return JsonResponse({'allocated': is_allocated})
    return JsonResponse({'error': 'Invalid employee code'}, status=400)

def fetch_buildings(request):
    camp_code = request.GET.get('camp_code')
    if camp_code:
        buildings = CampDetails.objects.filter(camp_code=camp_code).values_list('block', flat=True).distinct()
        return JsonResponse({'success': True, 'buildings': list(buildings)})
    return JsonResponse({'success': False, 'message': 'Invalid camp code.'}, status=400)

def fetch_floors(request):
    camp_code = request.GET.get('camp_code')
    building_name = request.GET.get('building_name')
    if camp_code and building_name:
        floors = CampDetails.objects.filter(camp_code=camp_code, block=building_name).values_list('floor', flat=True).distinct()
        return JsonResponse({'success': True, 'floors': list(floors)})
    return JsonResponse({'success': False, 'message': 'Invalid camp code or building name.'}, status=400)

def fetch_rooms(request):
    camp_code = request.GET.get('camp_code')
    building_name = request.GET.get('building_name')
    floor_no = request.GET.get('floor_no')
    if camp_code and building_name and floor_no:
        rooms = CampDetails.objects.filter(camp_code=camp_code, block=building_name, floor=floor_no).values_list('room_no', flat=True)
        return JsonResponse({'success': True, 'rooms': list(rooms)})
    return JsonResponse({'success': False, 'message': 'Invalid camp code, building name, or floor number.'}, status=400)

def fetch_beds(request):
    camp_code = request.GET.get('camp_code')
    building_name = request.GET.get('building_name')
    floor_no = request.GET.get('floor_no')
    room_no = request.GET.get('room_no')

    if camp_code and building_name and floor_no and room_no:
        # Fetch available beds from CampBeds where bed_status = 'N'
        available_beds = CampBeds.objects.filter(
            camp_code=camp_code,
            block=building_name,
            floor=floor_no,
            room_no=room_no,
            bed_status='N'  # Only fetch beds with status 'N'
        ).values_list('bed_no', flat=True)

        return JsonResponse({'success': True, 'beds': list(available_beds)})

    return JsonResponse({'success': False, 'message': 'Invalid room details.'}, status=400)

def check_bed_allocation(request):
    camp_code = request.GET.get('camp_code')
    building_name = request.GET.get('building_name')
    floor_no = request.GET.get('floor_no')
    room_no = request.GET.get('room_no')
    bed_no = request.GET.get('bed_no')

    if camp_code and building_name and floor_no and room_no and bed_no:
        is_allocated_current = CampAllocation.objects.filter(
            current_camp=camp_code,
            current_building=building_name,
            current_floor_no=floor_no,
            current_room_no=room_no,
            current_bed_no=bed_no
        ).exists()

        is_allocated_future = CampAllocation.objects.filter(
            camp=camp_code,
            building_name=building_name,
            floor_no=floor_no,
            room_no=room_no,
            bed_no=bed_no
        ).exists()
        return JsonResponse({'allocated_current': is_allocated_current,'allocated_future':is_allocated_future})
    return JsonResponse({'error': 'Invalid bed details.'}, status=400)

def camp_allocation_create(request):
    set_comp_code(request)  # Make sure this sets COMP_CODE globally or in session

    if request.method == 'POST':
        data = request.POST

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'REQCA'])
                result = cursor.fetchone()
                request_id = result[0] if result else None
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        try:
            CampAllocation.objects.create(
                request_id=request_id,
                comp_code=COMP_CODE,
                action_type=data.get('action_type'),
                employee_code=data.get('employee_code'),
                employee_name=data.get('employee_name'),
                camp=data.get('camp'),
                building_name=data.get('building_name'),
                floor_no=data.get('floor_no'),
                room_no=data.get('room_no'),
                bed_no=data.get('bed_no'),
                effective_date=data.get('effective_date') or None,
                reason=data.get('reason'),
                operational_approval='Pending',
                current_camp=data.get('current_camp'),
                current_building=data.get('current_building'),
                current_floor_no=data.get('current_floor_no'),
                current_room_no=data.get('current_room_no'),
                current_bed_no=data.get('current_bed_no'),
                exit_date=data.get('exit_date') or None,
                created_by=request.user.id if request.user.is_authenticated else 1,
                created_on=datetime.now(),
                modified_by=None,
                modified_on=datetime.now()
            )

            # Update the bed status to 'R' (Reserved)
            CampBeds.objects.filter(
                camp_code=data.get('camp'),
                block=data.get('building_name'),
                floor=data.get('floor_no'),
                room_no=data.get('room_no'),
                bed_no=data.get('bed_no')
            ).update(bed_status='R')

            return redirect('camp_allocation_list')

        except Exception as e:
            return JsonResponse({"error": f"Data insert failed: {str(e)}"}, status=500)

    return render(request, 'pages/payroll/camp_master/camp_transaction_form.html')

def camp_transaction_approval(request):
    set_comp_code(request)
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)

    # Filter transactions with operational_approval = 'Pending'
    pending_transactions = CampAllocation.objects.filter(operational_approval='Pending')
    if keyword:
        pending_transactions = pending_transactions.filter(
            Q(employee_code__icontains=keyword) |
            Q(employee_name__icontains=keyword) |
            Q(camp__icontains=keyword)
        )

    # Paginate the results
    paginator = Paginator(pending_transactions.order_by('-created_on'), PAGINATION_SIZE)
    try:
        transactions_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    return render(request, 'pages/payroll/camp_master/camp_transaction_approval.html', {
        'pending_transactions': transactions_page,
        'keyword': keyword,
    })

@csrf_exempt
def camp_transaction_approval_submit(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('approval_'):  # Check for approval fields
                transaction_id = key.split('_')[1]  # Extract transaction ID
                approval_status = value  # Get the approval value ('Yes' or 'No')

                # Update the operational_approval field
                camp_allow = CampAllocation.objects.filter(transaction_id=transaction_id)
                camp_allow.update(
                    operational_approval='Yes' if approval_status == 'Yes' else 'No'
                )

                camp_obj = camp_allow.first()
                if camp_obj:
                    if approval_status == 'Yes':
                        # If approval is "Yes," update bed details
                        CampDetails.objects.filter(
                            camp_code=camp_obj.camp,
                            block=camp_obj.building_name,
                            floor=camp_obj.floor_no,
                            room_no=camp_obj.room_no
                        ).update(
                            occupied_beds=F('occupied_beds') + 1,
                            available_beds=F('total_beds') - F('occupied_beds') - 1
                        )

                        CampBeds.objects.filter(
                            camp_code=camp_obj.camp,
                            block=camp_obj.building_name,
                            floor=camp_obj.floor_no,
                            room_no=camp_obj.room_no,
                            bed_no=camp_obj.bed_no
                        ).update(bed_status='A', emp_code=camp_obj.employee_code)
                    elif approval_status == 'No':
                        # If approval is "No," reset the bed status to 'N'
                        CampBeds.objects.filter(
                            camp_code=camp_obj.camp,
                            block=camp_obj.building_name,
                            floor=camp_obj.floor_no,
                            room_no=camp_obj.room_no,
                            bed_no=camp_obj.bed_no
                        ).update(bed_status='N', emp_code=None)

        return redirect('camp_transaction_approval')  # Redirect back to the approval page

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def fetch_room_numbers(request):
    camp_code = request.GET.get('camp_code')
    if camp_code:
        rooms = CampDetails.objects.filter(camp_code=camp_code).values_list('room_no', flat=True)
        return JsonResponse({'success': True, 'rooms': list(rooms)})
    return JsonResponse({'success': False, 'message': 'Invalid camp code.'}, status=400)

def check_employee_allocation(request):
    employee_code = request.GET.get('employee_code')
    if employee_code:
        allocation = CampAllocation.objects.filter(employee_code=employee_code).last()
        if allocation and allocation.effective_date <= date.today():
            return JsonResponse({
                'allocated': True,
                'current_camp': allocation.camp,
                'current_building': allocation.building_name,
                'current_floor_no': allocation.floor_no,
                'current_room_no': allocation.room_no,
                'current_bed_no': allocation.bed_no,
            })
        return JsonResponse({'allocated': False})
    return JsonResponse({'error': 'Invalid employee code'}, status=400)

def party_master_list(request):
    set_comp_code(request)
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all parties or filter by keyword
    if keyword:
        parties = PartyMaster.objects.filter(
            Q(customer_code__icontains=keyword) |
            Q(customer_name__icontains=keyword) |
            Q(contact_person__icontains=keyword)
        ).order_by('-party_id')
    else:
        parties = PartyMaster.objects.filter(comp_code=COMP_CODE).order_by('-party_id')

    # Handle Excel upload
    if request.method == 'POST' and 'excel_file' in request.FILES:
        try:
            df = pd.read_excel(request.FILES['excel_file'])
            valid_records = []
            invalid_records = []
            
            for index, row in df.iterrows():
                try:
                    # Validate required fields
                    required_fields = ['Customer Code*', 'Customer Name*', 'Telephone*', 'Contact Person*', 'Party Type*', 'Status*']
                    for field in required_fields:
                        if pd.isna(row[field]) or str(row[field]).strip() == '':
                            raise ValueError(f"Required field '{field}' is empty")
                    
                    # Validate status
                    status = str(row['Status*']).strip().upper()
                    if status not in ['ACTIVE', 'INACTIVE']:
                        raise ValueError(f"Invalid status '{status}'. Must be 'Active' or 'Inactive'")
                    
                    # Validate party type
                    party_type = str(row['Party Type*']).strip().upper()
                    if party_type not in ['CUSTOMER', 'VENDOR', 'BOTH']:
                        raise ValueError(f"Invalid party type '{party_type}'. Must be 'Customer', 'Vendor', or 'Both'")
                    
                    # Check if customer code already exists
                    if PartyMaster.objects.filter(customer_code=row['Customer Code*']).exists():
                        raise ValueError(f"Customer code '{row['Customer Code*']}' already exists")
                    
                    # Prepare record for preview
                    record = {
                        'row': index + 2,  # Excel rows start at 1, and we have a header
                        'customer_code': row['Customer Code*'],
                        'customer_name': row['Customer Name*'],
                        'contact_person': row['Contact Person*'],
                        'telephone': row['Telephone*'],
                        'email': row['Email'] if not pd.isna(row['Email']) else '',
                        'status': row['Status*']
                    }
                    valid_records.append(record)
                    
                except Exception as e:
                    invalid_records.append({
                        'row': index + 2,
                        'error': str(e)
                    })
            
            if request.POST.get('preview'):
                return JsonResponse({
                    'status': 'preview',
                    'total_records': len(df),
                    'valid_records': valid_records,
                    'invalid_records': invalid_records
                })
            
            if request.POST.get('confirm_upload'):
                # Create parties in database
                for record in valid_records:
                    PartyMaster.objects.create(
                        comp_code=COMP_CODE,
                        customer_code=record['customer_code'],
                        customer_name=record['customer_name'],
                        contact_person=record['contact_person'],
                        telephone=record['telephone'],
                        email=record['email'],
                        status=record['status']
                    )
                return JsonResponse({'status': 'success', 'message': 'Parties uploaded successfully'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    # Pagination
    paginator = Paginator(parties, 10)  # Show 10 parties per page
    page = request.GET.get('page', 1)
    try:
        parties = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        parties = paginator.page(1)
    
    # Calculate start and end indices for the current page
    start_index = (parties.number - 1) * paginator.per_page + 1
    end_index = min(start_index + paginator.per_page - 1, paginator.count)
    parties.start_index = start_index
    parties.end_index = end_index
    
    context = {
        'parties': parties,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else request.path + '?'
    }
    
    return render(request, 'pages/payroll/party_master/party_master.html', context)

def create_party(request):
    set_comp_code(request)
    if request.method == 'POST':
        comp_code = COMP_CODE

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'PARTY'])
                result = cursor.fetchone()
                customer_code = result[0] if result else None
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        # customer_code = request.POST.get('customer_code')
        customer_name = request.POST.get('customer_name')
        trade_license = request.POST.get('trade_license')
        physical_address = request.POST.get('physical_address')
        po_box = request.POST.get('po_box')
        emirates = ':'.join(request.POST.getlist('emirates'))
        country = request.POST.get('country')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')
        contact_person = request.POST.get('contact_person')
        contact_person_phone = request.POST.get('contact_person_phone')
        contact_person_email = request.POST.get('contact_person_email')
        tax_treatment = request.POST.get('tax_treatment')
        vat_no = request.POST.get('vat_no')
        currency = request.POST.get('currency')
        payment_terms = request.POST.get('payment_terms')
        status = request.POST.get('status')
        party_type = request.POST.get('party_type')
        upload_document = request.FILES.getlist('file_upload[]')

        if upload_document:
            for file in upload_document:
                PartyDocuments.objects.create(
                    comp_code=comp_code,
                    customer_code=customer_code,
                    document_name=file.name,
                    document_file=file
                )


        PartyMaster.objects.create(
            comp_code = COMP_CODE,
            customer_code=customer_code,
            customer_name=customer_name,
            trade_license=trade_license,
            physical_address=physical_address,
            po_box=po_box,
            emirates=emirates,
            country=country,
            telephone=telephone,
            email=email,
            contact_person=contact_person,
            contact_person_phone=contact_person_phone,
            contact_person_email=contact_person_email,
            tax_treatment=tax_treatment,
            vat_no=vat_no,
            currency=currency,
            payment_terms=payment_terms,
            status=status,
            party_type=party_type
        )
        return redirect('party_master_list')

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
@csrf_exempt
def party_master_edit(request):
    set_comp_code(request)
    if request.method == 'GET':
        party_id = request.GET.get('party_id')

        try:
            party = PartyMaster.objects.get(party_id=party_id)
            documents = PartyDocuments.objects.filter(customer_code=party.customer_code)

            # Prepare the response data
            document_data = [
                {
                    'document_name': doc.document_name,
                    'document_url': doc.document_file.url,  # Ensure MEDIA_URL is configured
                }
                for doc in documents
            ]

            return JsonResponse({
                'party_id': party.party_id,
                'customer_code': party.customer_code,
                'customer_name': party.customer_name,
                'trade_license': party.trade_license,
                'physical_address': party.physical_address,
                'po_box': party.po_box,
                'emirates': party.emirates,
                'country': party.country,
                'telephone': party.telephone,
                'email': party.email,
                'contact_person': party.contact_person,
                'contact_person_phone': party.contact_person_phone,
                'contact_person_email': party.contact_person_email,
                'tax_treatment': party.tax_treatment,
                'vat_no': party.vat_no,
                'currency': party.currency,
                'payment_terms': party.payment_terms,
                'status': party.status,
                'party_type': party.party_type,
                'documents': document_data,  # Include document data
            })
        except PartyMaster.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Party not found.'}, status=404)
        
    if request.method == 'POST':
        party_id = request.POST.get('party_id')

        try:
            party = PartyMaster.objects.get(party_id=party_id)
            party.customer_code = request.POST.get('customer_code')
            party.customer_name = request.POST.get('customer_name')
            party.trade_license = request.POST.get('trade_license')
            party.physical_address = request.POST.get('physical_address')
            party.po_box = request.POST.get('po_box')
            party.emirates = ':'.join(request.POST.getlist('emirates'))
            party.country = request.POST.get('country')
            party.telephone = request.POST.get('telephone')
            party.email = request.POST.get('email')
            party.contact_person = request.POST.get('contact_person')
            party.contact_person_phone = request.POST.get('contact_person_phone')
            party.contact_person_email = request.POST.get('contact_person_email')
            party.tax_treatment = request.POST.get('tax_treatment')
            party.vat_no = request.POST.get('vat_no')
            party.currency = request.POST.get('currency')
            party.payment_terms = request.POST.get('payment_terms')
            party.status = request.POST.get('status')
            party.party_type = request.POST.get('party_type')
            party.modified_by = request.user.id if request.user.is_authenticated else 1
            upload_document = request.FILES.getlist('file_upload[]')

            if upload_document:
                for file in upload_document:
                    PartyDocuments.objects.create(
                        comp_code=COMP_CODE,
                        customer_code=party.customer_code,
                        document_name=file.name,
                        document_file=file
                    )
            party.save()

            return redirect('party_master_list')
        except PartyMaster.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Party not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return redirect('party_master_list')

def delete_party(request, party_id):
    if request.method == 'POST':
        party = get_object_or_404(PartyMaster, party_id=party_id)
        party.delete()
        return JsonResponse({'success': True, 'message': 'Party deleted successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

def salary_register_single_line(request):
    set_comp_code(request)  # Ensure the company code is set
    return render(request, 'pages/modal/reports/salary_register_single.html')

def submit_salary_register(request):
    if request.method == 'POST':
        # Get form data
        employee_id = request.POST.get('employee_id')
        month = request.POST.get('month')

        # Validate input
        if not employee_id or not month:
            return JsonResponse({'success': False, 'message': 'Employee ID and Month are required.'}, status=400)

        # JasperReports server details
        jasper_url = 'http://<jasper-server-url>/jasperserver/rest_v2/reports/<report-path>'
        username = '<jasper-username>'
        password = '<jasper-password>'

        # Report parameters
        params = {
            'employee_id': employee_id,
            'month': month,
            'output': 'pdf'  # Specify the output format (e.g., pdf, xls, etc.)
        }

        # Encode parameters
        query_string = urllib.parse.urlencode(params)
        full_url = f"{jasper_url}?{query_string}"

        try:
            # Create a password manager for basic authentication
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, jasper_url, username, password)
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

            # Send the request
            with urllib.request.urlopen(full_url) as response:
                if response.status == 200:
                    # Return the report as a downloadable file
                    response_content = response.read()
                    response_headers = {
                        'Content-Type': 'application/pdf',
                        'Content-Disposition': f'attachment; filename="Salary_Register_{employee_id}_{month}.pdf"'
                    }
                    return HttpResponse(response_content, headers=response_headers)
                else:
                    return JsonResponse({'success': False, 'message': 'Failed to generate report. Please try again.'}, status=response.status)

        except urllib.error.URLError as e:
            return JsonResponse({'success': False, 'message': f'Error connecting to JasperReports server: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


def employee_enquiries(request):
    set_comp_code(request)  # Ensure the company code is set in the session

    # Fetch employees based on search keyword
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)

    # Initialize the query
    query = Employee.objects.filter(comp_code=COMP_CODE)

    # Apply search filter if a keyword is provided
    if keyword:
        query = query.filter(
            Q(emp_code__icontains=keyword) |
            Q(emp_name__icontains=keyword) |
            Q(department__icontains=keyword)
        )

    # Apply pagination
    paginator = Paginator(query.order_by('emp_code'), PAGINATION_SIZE)
    try:
        employees_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        employees_page = paginator.page(1)
    except EmptyPage:
        employees_page = paginator.page(paginator.num_pages)

    # Prepare the context for the template
    context = {
        'employees': employees_page,
        'keyword': keyword,
        'result_cnt': query.count(),
    }

    return render(request, 'pages/modal/enquiries/employee_enquiries.html', context)


def attendance_enquiries(request):
    set_comp_code(request)  # Ensure the company code is set in the session

    # Fetch attendance records based on search keyword
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)

    # Initialize the query
    query = WorkerAttendanceRegister.objects.filter(comp_code=COMP_CODE)

    # Apply search filter if a keyword is provided
    if keyword:
        query = query.filter(
            Q(employee_code__icontains=keyword) |
            Q(project_code__icontains=keyword) |
            Q(attendance_type__icontains=keyword)
        )

    # Apply pagination
    paginator = Paginator(query.order_by('date'), PAGINATION_SIZE)
    try:
        attendance_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        attendance_page = paginator.page(1)
    except EmptyPage:
        attendance_page = paginator.page(paginator.num_pages)

    # Prepare the context for the template
    context = {
        'attendance_records': attendance_page,
        'keyword': keyword,
        'result_cnt': query.count(),
    }

    return render(request, 'pages/modal/enquiries/attendance_enquiries.html', context)

def documents_enquiries(request):
    set_comp_code(request)

    category = request.GET.get('category', 'employee_document')
    keyword = request.GET.get('keyword', '').strip()

    employee_documents = dependent_documents = camp_documents = party_documents = license_and_passes = []

    if category == 'employee_document':
        employee_documents = EmployeeDocument.objects.filter(comp_code=COMP_CODE)
        if keyword:
            employee_documents = employee_documents.filter(
                Q(emp_code__icontains=keyword) |
                Q(document_type__icontains=keyword)
            )

    elif category == 'dependent_document':
        dependent_documents = EmployeeDocument.objects.filter(comp_code=COMP_CODE, relationship__isnull=False)
        if keyword:
            dependent_documents = dependent_documents.filter(
                Q(emp_code__icontains=keyword) |
                Q(relationship__icontains=keyword) |
                Q(document_type__icontains=keyword)
            )

    elif category == 'license_and_passes':
        license_and_passes = EmployeeDocument.objects.filter(comp_code=COMP_CODE, relationship__isnull=True, issued_date__isnull=True, emirates_issued_by__isnull=False)
        if keyword:
                license_and_passes = license_and_passes.filter(
                    Q(emp_code__icontains=keyword) |
                    Q(document_type__icontains=keyword)
                )

    elif category == 'camp_document':
        camp_documents = CampDocuments.objects.filter(comp_code=COMP_CODE)
        if keyword:
            camp_documents = camp_documents.filter(
                Q(camp_code__icontains=keyword) |
                Q(document_name__icontains=keyword)
            )

    elif category == 'party_document':
        party_documents = PartyDocuments.objects.filter(comp_code=COMP_CODE)
        if keyword:
            party_documents = party_documents.filter(
                Q(customer_code__icontains=keyword) |
                Q(document_name__icontains=keyword)
            )

    context = {
        'category': category,
        'keyword': keyword,
        'employee_documents': employee_documents,
        'dependent_documents': dependent_documents,
        'camp_documents': camp_documents,
        'party_documents': party_documents,
        'license_and_passes': license_and_passes
    }

    return render(request, 'pages/modal/enquiries/documents_enquiries.html', context)

from calendar import Calendar
from datetime import datetime
from django.shortcuts import render
from .models import Employee  # Ensure you have an Employee model

def duty_roster(request):
    month = request.GET.get('month')
    calendar_data = None
    employee_list = Employee.objects.all()  # Fetch all employees

    if month:
        # Parse the selected month
        year, month = map(int, month.split('-'))
        cal = Calendar()
        weeks = cal.monthdatescalendar(year, month)  # Get weeks with dates for the month

        # Prepare calendar data
        calendar_data = {
            'month': f"{datetime(year, month, 1):%B %Y}",  # Format as "Month Year"
            'weeks': [
                [
                    {'day': day.day, 'date': day.strftime('%Y-%m-%d')} if day.month == month else None
                    for day in week
                ]
                for week in weeks
            ],
        }

    context = {
        'calendar_data': calendar_data,
        'employee_list': employee_list,
    }
    return render(request, 'pages/payroll/duty_roster/duty_roster.html', context)

def download_project_template(request):
    # Create a DataFrame with the required columns
    df = pd.DataFrame(columns=[
        'Project Code*',
        'Project Name*',
        'Project Description*',
        'Project Type*',
        'Project Value*',
        'Start Date* (YYYY-MM-DD)',
        'End Date* (YYYY-MM-DD)',
        'Project City',
        'Service Type',
        'Service Category',
        'Project Sub Location',
        'Customer Code',
        'Agreement Ref',
        'OP Head Code',
        'Manager Code',
        'Commercial Manager Code',
        'Procurement User Code',
        'Indent User Code',
        'Final Contract Value',
        'Project Status'
    ])

    # Add example row with properly formatted dates
    current_date = datetime.now().strftime('%Y-%m-%d')
    next_year_date = (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')
    
    example_data = {
        'Project Code*': 'PRJ001',
        'Project Name*': 'Example Project',
        'Project Description*': 'This is an example project description',
        'Project Type*': 'CONSTRUCTION',
        'Project Value*': '100000.00',
        'Start Date* (YYYY-MM-DD)': current_date,
        'End Date* (YYYY-MM-DD)': next_year_date,
        'Project City': 'DUBAI:ABU DHABI',
        'Service Type': 'CONSTRUCTION',
        'Service Category': 'COMMERCIAL',
        'Project Sub Location': 'DOWNTOWN',
        'Customer Code': 'CUST001',
        'Agreement Ref': 'AGR001',
        'OP Head Code': 'EMP001:E001',
        'Manager Code': 'EMP002:E002',
        'Commercial Manager Code': 'EMP003:E003',
        'Procurement User Code': 'EMP004:E004',
        'Indent User Code': 'EMP005:E005',
        'Final Contract Value': '100000.00',
        'Project Status': 'ACTIVE'
    }
    df = pd.concat([df, pd.DataFrame([example_data])], ignore_index=True)

    # Create Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Projects', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Projects']
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        # Date format
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd'
        })
        
        # Format headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)  # Set column width
        
        # Add data validation for required fields
        required_cols = [col for col in df.columns if '*' in col]
        for col in required_cols:
            col_num = df.columns.get_loc(col)
            if 'Date' in col:
                # Date validation
                worksheet.data_validation(1, col_num, 1000, col_num, {
                    'validate': 'date',
                    'criteria': '>=',
                    'value': '1900-01-01',
                    'error_message': 'Please enter a valid date in YYYY-MM-DD format'
                })
                # Apply date format to the column
                worksheet.set_column(col_num, col_num, 20, date_format)
            else:
                # Non-date validation
                worksheet.data_validation(1, col_num, 1000, col_num, {
                    'validate': 'not_blank',
                    'error_message': 'This field is required'
                })

    # Set up the response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=project_template.xlsx'
    
    return response

# Leave Transaction Views
def leave_transaction_list(request):
    set_comp_code(request)
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all leave transactions or filter by keyword
    if keyword:
        leaves = LeaveTransaction.objects.filter(
            Q(employee_name__icontains=keyword) |
            Q(department__icontains=keyword) |
            Q(leave_type__icontains=keyword)
        ).order_by('-date_of_application')
    else:
        leaves = LeaveTransaction.objects.filter(comp_code=COMP_CODE).order_by('-date_of_application')
    
    employees = Employee.objects.filter(comp_code=COMP_CODE, emp_status='ACTIVE').values(
        'emp_code',
        'emp_name',
        'department',
        'designation',
        'date_of_join',
        'date_of_rejoin'
    )

    leave_types = LeaveMaster.objects.filter(comp_code=COMP_CODE).order_by('leave_code')
    context = {
        'leaves': leaves,
        'keyword': keyword,
        'result_cnt': leaves.count(),
        'employees': employees,
        'leave_types': leave_types
    }
    
    return render(request, 'pages/payroll/leave_master/leave_transaction_list.html', context)

@csrf_exempt
def leave_transaction_add(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create new leave transaction
                leave = LeaveTransaction.objects.create(
                    comp_code=request.session.get('comp_code', '1000'),
                    tran_id=generate_transaction_id('LEAVE'),
                    employee=request.POST.get('employee'),
                    employee_name=request.POST.get('employee_name'),
                    department=request.POST.get('department'),
                    designation=request.POST.get('designation'),
                    date_of_application=request.POST.get('date_of_application'),
                    leave_type=request.POST.get('leave_type'),
                    eligible_leave_days=request.POST.get('eligible_leave_days'),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date'),
                    total_leave_days=request.POST.get('total_leave_days'),
                    reason_for_leave=request.POST.get('reason_for_leave'),
                    contact_during_leave=request.POST.get('contact_during_leave'),
                    leave_policy_agreed=bool(request.POST.get('leave_policy_agreed')),
                    delegate_person=request.POST.get('delegate_person')
                )
                
                # Handle file upload if present
                if 'supporting_document' in request.FILES:
                    leave.supporting_document = request.FILES['supporting_document']
                    leave.save()

            return JsonResponse({'status': 'success', 'message': 'Leave transaction added successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def leave_transaction_edit(request):
    if request.method == 'GET':
        leave_id = request.GET.get('id')
        try:
            leave = get_object_or_404(LeaveTransaction, id=leave_id)
            data = {
                'status': 'success',
                'data': {
                    'id': leave.id,
                    'employee': leave.employee,
                    'employee_name': leave.employee_name,
                    'department': leave.department,
                    'designation': leave.designation,
                    'date_of_application': leave.date_of_application.strftime('%Y-%m-%d'),
                    'leave_type': leave.leave_type,
                    'eligible_leave_days': leave.eligible_leave_days,
                    'start_date': leave.start_date.strftime('%Y-%m-%d'),
                    'end_date': leave.end_date.strftime('%Y-%m-%d'),
                    'total_leave_days': leave.total_leave_days,
                    'reason_for_leave': leave.reason_for_leave,
                    'contact_during_leave': leave.contact_during_leave,
                    'leave_policy_agreed': leave.leave_policy_agreed,
                    'delegate_person': leave.delegate_person,
                    'supporting_document': leave.supporting_document.url if leave.supporting_document else None,
                    'supervisor_status': leave.supervisor_status,
                    'dept_head_status': leave.dept_head_status,
                    'hr_status': leave.hr_status
                }
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                leave_id = request.POST.get('leave_id')
                leave = get_object_or_404(LeaveTransaction, id=leave_id)
                
                # Update leave transaction
                leave.employee = request.POST.get('employee')
                leave.employee_name = request.POST.get('employee_name')
                leave.department = request.POST.get('department')
                leave.designation = request.POST.get('designation')
                leave.date_of_application = request.POST.get('date_of_application')
                leave.leave_type = request.POST.get('leave_type')
                leave.eligible_leave_days = request.POST.get('eligible_leave_days')
                leave.start_date = request.POST.get('start_date')
                leave.end_date = request.POST.get('end_date')
                leave.total_leave_days = request.POST.get('total_leave_days')
                leave.reason_for_leave = request.POST.get('reason_for_leave')
                leave.contact_during_leave = request.POST.get('contact_during_leave')
                leave.leave_policy_agreed = bool(request.POST.get('leave_policy_agreed'))
                leave.delegate_person = request.POST.get('delegate_person')
                
                # Handle file upload if present
                if 'supporting_document' in request.FILES:
                    leave.supporting_document = request.FILES['supporting_document']
                
                leave.save()

            return JsonResponse({'status': 'success', 'message': 'Leave transaction updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def leave_transaction_delete(request):
    if request.method == 'POST':
        try:
            leave_id = request.POST.get('leave_id')
            leave = get_object_or_404(LeaveTransaction, id=leave_id)
            leave.delete()
            return JsonResponse({'status': 'success', 'message': 'Leave transaction deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_leave_master_details(request):
    if request.method == 'GET':
        leave_type = request.GET.get('leave_type')
        try:
            leave_master = LeaveMaster.objects.filter(leave_code=leave_type).first()
            if leave_master:
                data = {
                    'leave_code': leave_master.leave_code,
                    'description': leave_master.description,
                    'eligible_days': leave_master.eligible_days,
                    'eligible_day_type': leave_master.eligible_day_type,
                    'payment_type': leave_master.payment_type,
                    'frequency': leave_master.frequency,
                    'gender': leave_master.gender,
                    'carry_forward': leave_master.carry_forward,
                    'encashment': leave_master.encashment,
                }
                return JsonResponse({'status': 'success', 'data': data})
            return JsonResponse({'status': 'error', 'message': 'Leave type not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def generate_transaction_id(prefix):
    # Get the current date in YYMM format
    current_date = timezone.now().strftime('%y%m')
    
    # Get the last transaction ID for this prefix and date
    last_transaction = LeaveTransaction.objects.filter(
        tran_id__startswith=f'{prefix}{current_date}'
    ).order_by('-tran_id').first()
    
    if last_transaction:
        # Extract the sequence number and increment it
        last_sequence = int(last_transaction.tran_id[-4:])
        new_sequence = last_sequence + 1
    else:
        # Start with 1 if no previous transaction
        new_sequence = 1
    
    # Format the new transaction ID
    return f'{prefix}{current_date}{new_sequence:04d}'

def leave_approval_list(request):
    """View for listing leave approvals"""
    keyword = request.GET.get('keyword', '')
    filter_type = request.GET.get('filter', 'all')
    
    leaves = LeaveTransaction.objects.all()
    
    if keyword:
        leaves = leaves.filter(
            Q(employee_name__icontains=keyword) |
            Q(department__icontains=keyword) |
            Q(leave_type__icontains=keyword)
        )
    
    if filter_type == 'supervisor':
        leaves = leaves.filter(supervisor_status='Pending')
    elif filter_type == 'dept_head':
        leaves = leaves.filter(supervisor_status='Approved', dept_head_status='Pending')
    elif filter_type == 'hr':
        leaves = leaves.filter(dept_head_status='Approved', hr_status='Pending')
    
    context = {
        'leaves': leaves,
        'keyword': keyword,
        'result_cnt': leaves.count()
    }
    return render(request, 'pages/payroll/leave_master/leave_approval_list.html', context)

@csrf_exempt
def leave_approval(request):
    """View for handling leave approvals"""
    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        role = request.POST.get('role')
        action = request.POST.get('action')
        comments = request.POST.get('comments')
        
        try:
            leave = LeaveTransaction.objects.get(id=leave_id)
            
            if role == 'supervisor' and action == 'approve':
                leave.supervisor_status = 'Approved' if action == 'approve' else 'Rejected'
                leave.supervisor_approval_date = timezone.now()
                leave.supervisor_comments = comments
            elif role == 'dept_head' and action == 'approve':
                leave.dept_head_status = 'Approved' if action == 'approve' else 'Rejected'
                leave.dept_head_approval_date = timezone.now()
                leave.dept_head_comments = comments
            elif role == 'hr' and action == 'approve':
                leave.hr_status = 'Approved' if action == 'approve' else 'Rejected'
                leave.hr_approval_date = timezone.now()
                leave.hr_comments = comments
            elif role == 'cancel' and action == 'cancel':
                # Update all statuses to Cancelled
                leave.supervisor_status = 'Cancelled'
                leave.dept_head_status = 'Cancelled'
                leave.hr_status = 'Cancelled'
                # Add a flag to indicate the leave is cancelled
                leave.is_cancelled = True
                leave.cancellation_date = timezone.now()
                leave.cancellation_comments = comments
            
            leave.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Leave {action}d successfully'
            })
        except LeaveTransaction.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Leave not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

def download_party_template(request):
    # Create a DataFrame with the required columns
    df = pd.DataFrame(columns=[
        'Customer Code*',
        'Customer Name*',
        'Trade License',
        'Physical Address',
        'PO Box',
        'Telephone*',
        'Email',
        'Contact Person*',
        'Contact Person Phone',
        'Contact Person Email',
        'VAT No',
        'Emirates',
        'Country',
        'Tax Treatment',
        'Currency',
        'Payment Terms',
        'Party Type*',
        'Status*'
    ])

    # Add example row
    example_data = {
        'Customer Code*': 'CUST001',
        'Customer Name*': 'Example Company',
        'Trade License': 'TL123456',
        'Physical Address': '123 Business Street',
        'PO Box': '12345',
        'Telephone*': '+971501234567',
        'Email': 'contact@example.com',
        'Contact Person*': 'John Doe',
        'Contact Person Phone': '+971501234568',
        'Contact Person Email': 'john@example.com',
        'VAT No': '123456789012345',
        'Emirates': 'DUBAI',
        'Country': 'UAE',
        'Tax Treatment': 'STANDARD',
        'Currency': 'AED',
        'Payment Terms': '30 DAYS',
        'Party Type*': 'CUSTOMER',
        'Status*': 'Active'
    }
    df = pd.concat([df, pd.DataFrame([example_data])], ignore_index=True)

    # Create Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Parties', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Parties']
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        # Format headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)  # Set column width
        
        # Add data validation for required fields
        required_cols = [col for col in df.columns if '*' in col]
        for col in required_cols:
            col_num = df.columns.get_loc(col)
            worksheet.data_validation(1, col_num, 1000, col_num, {
                'validate': 'not_blank',
                'error_message': 'This field is required'
            })

    # Set up the response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=party_template.xlsx'
    
    return response

def attendance_correction(request):
    set_comp_code(request)
    try:
        comp_code = COMP_CODE
        if not comp_code:
            messages.error(request, 'Company code not found in session')
            return redirect('index')

        # Get all active employees
        employees = Employee.objects.filter(
            comp_code=comp_code,
            emp_status='ACTIVE'
        ).values('emp_code', 'emp_name', 'process_cycle')

        if not employees.exists():
            messages.error(request, 'No active employees found')
            return redirect('index')

        context = {
            'employees': employees
        }
        return render(request, 'pages/payroll/attendance_upload/attendance_correction.html', context)
    except Exception as e:
        messages.error(request, f'Error in attendance correction: {str(e)}')
        return redirect('index')

@csrf_exempt
def get_employee_process_cycle(request):
    set_comp_code(request)
    try:
        comp_code = COMP_CODE
        if not comp_code:
            return JsonResponse({'success': False, 'message': 'Company code not found in session'})

        employee = request.GET.get('employee')
        if not employee:
            return JsonResponse({'success': False, 'message': 'Employee code is required'})

        # Get employee's process cycle
        employee_data = Employee.objects.filter(
            comp_code=comp_code,
            emp_code=employee
        ).values('process_cycle').first()

        if not employee_data:
            return JsonResponse({'success': False, 'message': 'Employee not found'})


        # Get pay process month from PaycycleMaster
        paycycle = PaycycleMaster.objects.filter(
            comp_code=comp_code,
            process_cycle=employee_data['process_cycle'],  # Fixed typo in field name
            is_active='Y'
        ).order_by('-process_cycle_id').first()

        if not paycycle:
            return JsonResponse({'success': False, 'message': 'No active pay cycle found for this employee'})


        # Format the month as YYYY-MM
        pay_process_month = paycycle.pay_process_month

        return JsonResponse({
            'success': True,
            'process_cycle': employee_data['process_cycle'],
            'pay_process_month': pay_process_month
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def fetch_attendance_data(request):
    try:
        employee = request.GET.get('employee')
        month = request.GET.get('month')
        
        if not employee or not month:
            return JsonResponse({
                'success': False,
                'message': 'Employee and month are required'
            })

        # Fetch attendance records
        attendance_records = WorkerAttendanceRegister.objects.filter(
            employee_code=employee,
            pay_process_month=month
        ).order_by('date')

        attendance_data = []
        for record in attendance_records:
            attendance_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'day': record.date.strftime('%A'),
                'project_code': record.project_code,
                'morning': record.morning,
                'afternoon': record.afternoon,
                'ot1': record.ot1,
                'ot2': record.ot2,
                'in_time': record.in_time,
                'out_time': record.out_time
            })

        return JsonResponse({
            'success': True,
            'attendance': attendance_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@csrf_exempt
def save_attendance_correction(request):
    try:
        data = json.loads(request.body)
        employee = data.get('employee')
        month = data.get('month')
        attendance_data = data.get('attendance_data', [])

        if not employee or not month or not attendance_data:
            return JsonResponse({
                'success': False,
                'message': 'Required fields are missing'
            })

        for record in attendance_data:
            date_obj = datetime.strptime(record['date'], '%Y-%m-%d').date()
            in_time_obj = datetime.strptime(record['in_time'], '%H:%M').time() if record['in_time'] else None
            out_time_obj = datetime.strptime(record['out_time'], '%H:%M').time() if record['out_time'] else None

            # Calculate working hours if both times are provided
            working_hours = None
            if in_time_obj and out_time_obj:
                in_datetime = datetime.combine(date.today(), in_time_obj)
                out_datetime = datetime.combine(date.today(), out_time_obj)
                time_diff = out_datetime - in_datetime
                working_hours = time_diff.total_seconds() / 3600  # Convert to hours

            # Update or create attendance record
            WorkerAttendanceRegister.objects.update_or_create(
                employee_code=employee,
                pay_process_month=month,
                date=date_obj,
                defaults={
                    'project_code': record['project_code'],
                    'morning': record['morning'],
                    'afternoon': record['afternoon'],
                    'ot1': record['ot1'],
                    'ot2': record['ot2'],
                    'in_time': in_time_obj,
                    'out_time': out_time_obj,
                    'working_hours': working_hours
                }
            )

        return JsonResponse({
            'success': True,
            'message': 'Attendance updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def gratuity_list(request):
    set_comp_code(request)
    """View to display list of gratuity settlements"""
    # Get search keyword
    keyword = request.GET.get('keyword', '').strip()
    
    # Base queryset
    gratuity_list = GratuitySettlement.objects.filter(comp_code=COMP_CODE)
    
    # Apply search filter if keyword exists
    if keyword:
        gratuity_list = gratuity_list.filter(
            Q(employee_code__icontains=keyword) |
            Q(employee_name__icontains=keyword)
        )
    
    # Order by created date
    gratuity_list = gratuity_list.order_by('-created_on')
    
    # Get total count for pagination info
    result_cnt = gratuity_list.count()
    
    # Pagination
    paginator = Paginator(gratuity_list, PAGINATION_SIZE)  # Show 10 records per page
    page = request.GET.get('page')
    gratuity_list = paginator.get_page(page)
    
    # Get current URL for pagination links
    current_url = request.path
    
    return render(request, 'pages/payroll/graduity/graduity_list.html', {
        'gratuity_list': gratuity_list,
        'keyword': keyword,
        'result_cnt': result_cnt,
        'current_url': current_url
    });

@csrf_exempt
def add_gratuity(request):
    set_comp_code(request)
    """View to add new gratuity settlement"""
    if request.method == 'POST':
        try:
            # Get all form data
            employee_code = request.POST.get('employee_code')
            employee_name = request.POST.get('employee_name')
            category = request.POST.get('category')
            designation = request.POST.get('designation')
            date_of_joining = request.POST.get('date_of_joining')
            date_of_exit = request.POST.get('date_of_exit')
            total_years_of_service = request.POST.get('total_years_of_service')
            accrude_days = request.POST.get('acrude_days')
            loss_of_pay_days = request.POST.get('loss_of_pay_days')
            leave_balance_days = request.POST.get('leave_balance_days')
            leave_encashment_amount = request.POST.get('leave_encashment_amount')
            bonus_amount = request.POST.get('bonus_amount')
            other_allowances = request.POST.get('other_allowances')
            deductions = request.POST.get('deduction')
            other_deductions = request.POST.get('other_deduction')
            loan_recovery = request.POST.get('loan_recovery')
            notice_pay = request.POST.get('notice_pay')
            final_settlement_amount = request.POST.get('final_settlement_amount')
            last_drawn_basic_salary = request.POST.get('last_drawn_basic_salary')
            eligible_gratuity = request.POST.get('eligible_gratuity')
            gratuity_status = request.POST.get('gratuity_status')
            settlement_status = request.POST.get('settlement_status')
            payment_mode = request.POST.get('payment_mode')
            bank_name = request.POST.get('bank_name')
            bank_account_no = request.POST.get('bank_account_no')
            settlement_date = request.POST.get('settlement_date') or None   
            remarks = request.POST.get('remarks')
            supporting_docs = request.FILES.get('supporting_docs')
            attachments = request.FILES.get('attachment')
            
            # Create new gratuity settlement
            gratuity = GratuitySettlement.objects.create(
                comp_code=COMP_CODE,
                employee_code=employee_code,
                employee_name=employee_name,
                category=category,
                designation=designation,
                date_of_joining=date_of_joining,
                date_of_exit=date_of_exit,
                total_years_of_service=total_years_of_service,
                accrude_days=accrude_days,
                loss_of_pay_days=loss_of_pay_days,
                leave_balance_days=leave_balance_days,
                leave_encashment_amount=leave_encashment_amount,
                bonus_amount=bonus_amount,
                other_allowances=other_allowances,
                deductions=deductions,
                other_deductions=other_deductions,
                loan_recovery=loan_recovery,
                notice_pay=notice_pay,
                final_settlement_amount=final_settlement_amount,
                last_drawn_basic_salary=last_drawn_basic_salary,
                eligible_gratuity=eligible_gratuity,
                gratuity_status=gratuity_status,
                settlement_status=settlement_status,
                payment_mode=payment_mode,
                bank_name=bank_name,
                bank_account_no=bank_account_no,
                settlement_date=settlement_date,
                supporting_docs=supporting_docs,
                attachments=attachments,
                remarks=remarks,
                created_by=1
            )
            
            messages.success(request, 'Gratuity settlement added successfully!')
            return redirect('gratuity_list')
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@csrf_exempt
def update_gratuity(request):
    """View to update existing gratuity settlement"""
    set_comp_code(request)
    id = request.POST.get('id')
    if request.method == 'POST':
        try:
            gratuity = get_object_or_404(GratuitySettlement, id=id)
            
            # Update all fields
            gratuity.employee_code = request.POST.get('employee_code')
            gratuity.employee_name = request.POST.get('employee_name')
            gratuity.category = request.POST.get('category')
            gratuity.designation = request.POST.get('designation')
            gratuity.date_of_joining = request.POST.get('date_of_joining') or None
            gratuity.date_of_exit = request.POST.get('date_of_exit') or None
            gratuity.total_years_of_service = request.POST.get('total_years_of_service')
            gratuity.accrude_days = request.POST.get('acrude_days')
            gratuity.loss_of_pay_days = request.POST.get('loss_of_pay_days')
            gratuity.leave_balance_days = request.POST.get('leave_balance_days')
            gratuity.leave_encashment_amount = request.POST.get('leave_encashment_amount')
            gratuity.bonus_amount = request.POST.get('bonus_amount')
            gratuity.other_allowances = request.POST.get('other_allowances')
            gratuity.deductions = request.POST.get('deduction')
            gratuity.other_deductions = request.POST.get('other_deduction')
            gratuity.loan_recovery = request.POST.get('loan_recovery')
            gratuity.notice_pay = request.POST.get('notice_pay')
            gratuity.final_settlement_amount = request.POST.get('final_settlement_amount')
            gratuity.last_drawn_basic_salary = request.POST.get('last_drawn_basic_salary')
            gratuity.eligible_gratuity = request.POST.get('eligible_gratuity')
            gratuity.gratuity_status = request.POST.get('gratuity_status')
            gratuity.settlement_status = request.POST.get('settlement_status')
            gratuity.payment_mode = request.POST.get('payment_mode')
            gratuity.bank_name = request.POST.get('bank_name')
            gratuity.bank_account_no = request.POST.get('bank_account_no')
            gratuity.settlement_date = request.POST.get('settlement_date') or None
            gratuity.remarks = request.POST.get('remarks')
            gratuity.supporting_docs = request.FILES.get('supporting_docs') or gratuity.supporting_docs
            gratuity.attachments = request.FILES.get('attachments') or gratuity.attachments
            # gratuity.updated_by = request.user.id
            # gratuity.updated_at = timezone.now()
            
            gratuity.save()
            
            return redirect('gratuity_list')
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@csrf_exempt
def delete_gratuity(request, gratuity_id):
    """View to delete gratuity settlement"""
    if request.method == 'POST':
        try:
            gratuity = get_object_or_404(GratuitySettlement, id=gratuity_id)
            gratuity.delete()
            
            return redirect('gratuity_list')
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@csrf_exempt
def get_gratuity_details(request):
    """View to get gratuity settlement details for editing"""
    try:
        gratuity_id = request.GET.get('id')
        gratuity = get_object_or_404(GratuitySettlement, id=gratuity_id)
        data = {
            'status': 'success',
            'data': {
                'id': gratuity.id,
                'employee_code': gratuity.employee_code,
                'employee_name': gratuity.employee_name,
                'category': gratuity.category,
                'designation': gratuity.designation,
                'date_of_joining': gratuity.date_of_joining,
                'date_of_exit': gratuity.date_of_exit,
                'total_years_of_service': gratuity.total_years_of_service,
                'accrude_days': gratuity.accrude_days,
                'last_drawn_basic_salary': str(gratuity.last_drawn_basic_salary),
                'eligible_gratuity': str(gratuity.eligible_gratuity),
                'loss_of_pay_days': str(gratuity.loss_of_pay_days),
                'gratuity_status': gratuity.gratuity_status,
                'leave_balance_days': str(gratuity.leave_balance_days),
                'leave_encashment_amount': str(gratuity.leave_encashment_amount),
                'bonus_amount': str(gratuity.bonus_amount),
                'other_allowances': str(gratuity.other_allowances),
                'deduction': str(gratuity.deductions),
                'other_deduction': str(gratuity.other_deductions),
                'loan_recovery': str(gratuity.loan_recovery),
                'notice_pay': str(gratuity.notice_pay),
                'final_settlement_amount': str(gratuity.final_settlement_amount),
                'settlement_status': gratuity.settlement_status,
                'payment_mode': gratuity.payment_mode,
                'bank_name': gratuity.bank_name,
                'bank_account_no': gratuity.bank_account_no,
                'settlement_date': gratuity.settlement_date,
                'remarks': gratuity.remarks,
                'supporting_docs': gratuity.supporting_docs.url if gratuity.supporting_docs else None,
                'attachments': gratuity.attachments.url if gratuity.attachments else None
            }
        }        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def leave_master_list(request):
    set_comp_code(request)
    try:
        # Get search parameters
        keyword = request.GET.get('keyword', '')
        
        # Base query
        leaves = LeaveMaster.objects.filter(comp_code=COMP_CODE).order_by('leave_code')
        
        # Apply search filter if keyword exists
        if keyword:
            leaves = leaves.filter(
                Q(leave_code__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        # Get total count for pagination
        result_cnt = leaves.count()
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(leaves, PAGINATION_SIZE)  # Show 10 items per page
        
        try:
            leaves = paginator.page(page)
        except PageNotAnInteger:
            leaves = paginator.page(1)
        except EmptyPage:
            leaves = paginator.page(paginator.num_pages)
        
        # Get grade data for dropdown
        grade_data = GradeMaster.objects.filter(
            comp_code=COMP_CODE,
            is_active='Y'
        ).order_by('grade_code')
        
        context = {
            'leaves': leaves,
            'result_cnt': result_cnt,
            'keyword': keyword,
            'grade_data': grade_data,
            'current_url': request.path
        }
        
        return render(request, 'pages/payroll/leave_master/leave_master_list.html', context)
    except Exception as e:
        messages.error(request, f'Error loading leave master: {str(e)}')
        return redirect('leave_master_list')

def leave_master_create(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            # Get form data
            # leave_code = request.POST.get('leave_code')
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'LT'])
                    result = cursor.fetchone()
                    leave_code = result[0] if result else None
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
            leave_code = leave_code
            description = request.POST.get('description')
            work_month = request.POST.get('work_month')
            eligible_days = request.POST.get('eligible_days')
            eligible_day_type = request.POST.get('eligible_day_type')
            payment_type = request.POST.get('payment_type')
            frequency = request.POST.get('frequency')
            gender = request.POST.get('gender')
            grade = request.POST.getlist('grade')  # Get list of selected grades
            carry_forward = request.POST.get('carry_forward')
            carry_forward_period = request.POST.get('carry_forward_period')
            encashment = request.POST.get('encashment')
            is_active = request.POST.get('is_active') == 'Active'
            
            # Validate required fields
            # if not all([leave_code, description, work_month, eligible_days, eligible_day_type, 
            #            payment_type, frequency, gender, carry_forward, encashment]):
            #     messages.error(request, 'All required fields must be filled')
            #     return redirect('leave_master_list')
            
            # Create new leave type
            leave = LeaveMaster(
                comp_code=COMP_CODE,
                leave_code=leave_code,
                description=description,
                work_month=work_month,
                eligible_days=eligible_days,
                eligible_day_type=eligible_day_type,
                payment_type=payment_type,
                frequency=frequency,
                gender=gender,
                grade=','.join(grade) if grade else None,
                carry_forward=carry_forward,
                carry_forward_period=carry_forward_period if carry_forward == 'Yes' else None,
                encashment=encashment,
                is_active=is_active,
                created_by=1
            )
            leave.save()
            
            messages.success(request, 'Leave type created successfully!')
            return redirect('leave_master_list')
            
        except Exception as e:
            messages.error(request, f'Error creating leave type: {str(e)}')
            return redirect('leave_master_list')
    return redirect('leave_master_list')

@csrf_exempt
def check_leave_code(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            leave_code = request.POST.get('leave_code')
            exists = LeaveMaster.objects.filter(
                comp_code=COMP_CODE,
                leave_code=leave_code
            ).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_leave_details(request):
    set_comp_code(request)
    if request.method == 'GET':
        try:
            leave_id = request.GET.get('leave_id')
            leave = LeaveMaster.objects.get(
                comp_code=COMP_CODE,
                leave_id=leave_id
            )
            
            # Convert grade string to list
            grade_list = leave.grade.split(',') if leave.grade else []
            
            data = {
                'leave_id': leave.leave_id,
                'leave_code': leave.leave_code,
                'description': leave.description,
                'work_month': leave.work_month,
                'eligible_days': leave.eligible_days,
                'eligible_day_type': leave.eligible_day_type,
                'payment_type': leave.payment_type,
                'frequency': leave.frequency,
                'gender': leave.gender,
                'grade': grade_list,
                'carry_forward': leave.carry_forward,
                'carry_forward_period': leave.carry_forward_period,
                'encashment': leave.encashment,
                'is_active': leave.is_active
            }
            return JsonResponse(data)
        except LeaveMaster.DoesNotExist:
            return JsonResponse({'error': 'Leave type not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def update_leave_details(request):
    set_comp_code(request)
    leave_id = request.POST.get('leave_id')
    if request.method == 'POST':
        try:
            leave = LeaveMaster.objects.get(
                comp_code=COMP_CODE,
                leave_id=leave_id
            )
            
            # Update fields
            leave.description = request.POST.get('description')
            leave.work_month = request.POST.get('work_month')
            leave.eligible_days = request.POST.get('eligible_days')
            leave.eligible_day_type = request.POST.get('eligible_day_type')
            leave.payment_type = request.POST.get('payment_type')
            leave.frequency = request.POST.get('frequency')
            leave.gender = request.POST.get('gender')
            leave.grade = ','.join(request.POST.getlist('grade'))
            leave.carry_forward = request.POST.get('carry_forward')
            leave.carry_forward_period = request.POST.get('carry_forward_period') if request.POST.get('carry_forward') == 'Yes' else None
            leave.encashment = request.POST.get('encashment')
            leave.is_active = request.POST.get('is_active') == 'Active'
            leave.modified_by = request.session.get('user_id')
            leave.save()
            messages.success(request, 'Leave type updated successfully!')
            return redirect('leave_master_list')
            
        except LeaveMaster.DoesNotExist:
            return JsonResponse({'error': 'Leave type not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_leave_type(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            leave_id = request.POST.get('leave_id')
            leave = LeaveMaster.objects.get(
                comp_code=COMP_CODE,
                leave_id=leave_id
            )
            leave.delete()
            messages.success(request, 'Leave type deleted successfully!')
            return redirect('leave_master_list')
        except LeaveMaster.DoesNotExist:
            return JsonResponse({'error': 'Leave type not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def rejoin_approval_list(request):
    keyword = request.GET.get('keyword', '')
    page = request.GET.get('page', 1)
    
    # Base query for approved leaves
    leaves = LeaveTransaction.objects.filter(
        comp_code=COMP_CODE,
        supervisor_status='Approved',
        dept_head_status='Approved',
        hr_status='Approved'
    ).order_by('-start_date')
    
    # Apply search filter if keyword exists
    if keyword:
        leaves = leaves.filter(
            Q(employee__icontains=keyword) |
            Q(employee_name__icontains=keyword) |
            Q(leave_type__icontains=keyword)
        )
    
    # Pagination
    paginator = Paginator(leaves, 10)
    try:
        leaves = paginator.page(page)
    except PageNotAnInteger:
        leaves = paginator.page(1)
    except EmptyPage:
        leaves = paginator.page(paginator.num_pages)
    
    context = {
        'leaves': leaves,
        'keyword': keyword,
        'result_cnt': leaves.paginator.count
    }
    
    return render(request, 'pages/payroll/leave_master/rejoin_approval_list.html', context)

def get_rejoin_details(request):
    try:
        leave_id = request.GET.get('leave_id')
        leave = LeaveTransaction.objects.get(tran_id=leave_id, comp_code=COMP_CODE)
        data = {
            'employee_code': leave.employee,
            'employee_name': leave.employee_name,
            'leave_type': leave.leave_type,
            'start_date': leave.start_date.strftime('%Y-%m-%d'),
            'end_date': leave.end_date.strftime('%Y-%m-%d'),
            'actual_rejoin_date': leave.actual_rejoin_date.strftime('%Y-%m-%d') if leave.actual_rejoin_date else None,
            'rejoin_status': leave.rejoin_status,
            'remarks': leave.rejoin_remarks
        }
        return JsonResponse(data)
    except LeaveTransaction.DoesNotExist:
        return JsonResponse({'error': 'Leave not found'}, status=404)

@csrf_exempt
def rejoin_approval_submit(request):
    if request.method == 'POST':
        try:
            leave_id = request.POST.get('leave_id')
            leave = LeaveTransaction.objects.get(tran_id=leave_id, comp_code=COMP_CODE)
            
            # Update rejoin details
            leave.actual_rejoin_date = request.POST.get('actual_rejoin_date')
            leave.rejoin_status = request.POST.get('rejoin_status')
            leave.rejoin_remarks = request.POST.get('remarks')
            leave.approval_by = request.session.get('username')
            leave.modified_by = request.session.get('username')
            leave.modified_on = now()
            
            leave.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Rejoin approval updated successfully'
            })
        except LeaveTransaction.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Leave not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@csrf_exempt
def get_rejoin_notifications(request):
    set_comp_code(request)
    try:
        # Get today's and tomorrow's dates
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Get all leaves where end_date is today
        rejoin_notifications = LeaveTransaction.objects.filter(
            comp_code=COMP_CODE,
            end_date=today
        )
        
        notifications = []
        for leave in rejoin_notifications:
            notifications.append({
                'id': leave.tran_id,
                'employee_name': leave.employee_name,
                'department': leave.department,
                'rejoin_date': tomorrow.strftime('%d-%b-%Y'),  # Show tomorrow as rejoin date
                'leave_type': leave.leave_type,
                'end_date': leave.end_date.strftime('%d-%b-%Y'),
                'status': leave.rejoin_status or 'Pending'  # Show current status
            })
        
        return JsonResponse({
            'status': 'success',
            'notifications': notifications,
            'count': len(notifications)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def get_emp_code(request):
    set_comp_code(request)
    if request.method == 'GET':
        try:
            emp_code = request.GET.get('emp_code')
            if not emp_code:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Employee code is required'
                }, status=400)

            # Fetch employee details from EmployeeMaster
            employee = Employee.objects.filter(
                emp_code=emp_code,
                comp_code=COMP_CODE
            ).first()

            if not employee:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Employee not found'
                }, status=404)

            # Format the response data
            response_data = {
                'status': 'success',
                'data': {
                    'emp_code': employee.emp_code,
                    'category': employee.staff_category,
                    'designation': employee.designation,
                    'date_of_joining': employee.date_of_join.strftime('%Y-%m-%d') if employee.date_of_join else None,
                    'basic_salary': float(employee.basic_pay) if employee.basic_pay else 0.00
                }
            }
            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)
    

def ao_entry_list(request):
    set_comp_code(request)
    keyword = request.GET.get('keyword', '')
    entries = Recruitment.objects.filter(comp_code=COMP_CODE).order_by('-ao_ref_no')
    mrf_data = MRFMaster.objects.filter(comp_code=COMP_CODE, status='Open', remaining_quantity__gt=0)
    
    if keyword:
        entries = entries.filter(
            Q(name_as_per_pp__icontains=keyword) |
            Q(ao_ref_no__icontains=keyword) |
            Q(project__icontains=keyword) |
            Q(dep__icontains=keyword)
        )
    
    # Pagination
    paginator = Paginator(entries, PAGINATION_SIZE)  # Show 10 entries per page
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    
    context = {
        'entries': entries,
        'result_cnt': entries.paginator.count if entries else 0,
        'keyword': keyword,
        'mrf_data': mrf_data
    }
    return render(request, 'pages/payroll/recruitment/ao_entry_list.html', context)

@csrf_exempt
def ao_entry_create(request):
    set_comp_code(request)
    if request.method == 'POST':
            ao_issued_date = request.POST.get('ao_issued_date') or None
            dep = request.POST.get('dep')
            project = request.POST.get('project')
            mrf = request.POST.get('mrf')
            category = request.POST.get('category')
            # ao_ref_no = request.POST.get('ao_ref_no')
            name_as_per_pp = request.POST.get('name_as_per_pp')
            pp_number = request.POST.get('pp_number')
            pp_exp_date = request.POST.get('pp_exp_date') or None
            pp_validity_days = request.POST.get('pp_validity_days')
            dob = request.POST.get('dob') or None
            age = request.POST.get('age')
            nationality = request.POST.get('nationality')
            agent = request.POST.get('agent')
            designation = request.POST.get('designation')
            gender = request.POST.get('gender')
            employee_status = request.POST.get('employee_status')
            grade = request.POST.get('grade')
            basic = request.POST.get('basic')
            hra = request.POST.get('hra')
            transportation_allowance = request.POST.get('transportation_allowance')
            accommodation = request.POST.get('accommodation')
            telephone = request.POST.get('telephone')
            additional_duty_allowance = request.POST.get('additional_duty_allowance')
            other_allowance = request.POST.get('other_allowance')
            total = request.POST.get('total')
            in_words = request.POST.get('in_words')
            ao_acceptance = request.POST.get('ao_acceptance')
            acceptance_date = request.POST.get('acceptance_date') or None
            document_status = request.POST.get('document_status')
            interview_date = request.POST.get('interview_date') or None

            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'AO'])
                    result = cursor.fetchone()
                    ao_ref_no = result[0] if result else None
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
            
            try: 
                recruitment = Recruitment.objects.create(
                    comp_code=COMP_CODE,
                    ao_issued_date=ao_issued_date,
                    dep=dep,
                    project=project,
                    mrf=mrf,
                    category=category,
                    ao_ref_no=ao_ref_no,
                    name_as_per_pp=name_as_per_pp,
                    pp_number=pp_number,
                    pp_exp_date=pp_exp_date,
                    pp_validity_days=pp_validity_days,
                    dob=dob,
                    age=age,
                    nationality=nationality,
                    agent=agent,
                    designation=designation,
                    gender=gender,
                    employee_status=employee_status,
                    grade=grade,
                    basic=basic,
                    hra=hra,
                    transportation_allowance=transportation_allowance,
                    accommodation=accommodation,
                    telephone=telephone,
                    additional_duty_allowance=additional_duty_allowance,
                    other_allowance=other_allowance,
                    total=total,
                    in_words=in_words,
                    ao_acceptance=ao_acceptance,
                    acceptance_date=acceptance_date,
                    document_status=document_status,
                    interview_date=interview_date,
                    # created_by=request.session.get('username'),
                    # created_on=now()
                )
                mrf_data = MRFMaster.objects.get(comp_code=COMP_CODE, id=mrf)
                remaining_quantity = int(mrf_data.remaining_quantity) - 1
                mrf_data.remaining_quantity = remaining_quantity
                mrf_data.save()
                messages.success(request, 'AO Entry created successfully!')
                return redirect('ao_entry_list')
            
            except Exception as e:
                messages.error(request, f'Error creating AO Entry: {str(e)}')
                return redirect('ao_entry_list')
    return redirect('ao_entry_list')

def ao_entry_edit(request):
    set_comp_code(request)
    if request.method == 'GET':
        try:
            ao_entry_id = request.GET.get('ao_entry_id')
            ao_entry = Recruitment.objects.get(recr_id=ao_entry_id, comp_code=COMP_CODE)
            data = {
                'recr_id': ao_entry.recr_id,
                'ao_issued_date': ao_entry.ao_issued_date.strftime('%Y-%m-%d') if ao_entry.ao_issued_date else None,
                'dep': ao_entry.dep,
                'project': ao_entry.project,
                'mrf': ao_entry.mrf,
                'category': ao_entry.category,
                'ao_ref_no': ao_entry.ao_ref_no,
                'name_as_per_pp': ao_entry.name_as_per_pp,
                'pp_number': ao_entry.pp_number,
                'pp_exp_date': ao_entry.pp_exp_date.strftime('%Y-%m-%d') if ao_entry.pp_exp_date else None,
                'pp_validity_days': ao_entry.pp_validity_days,
                'dob': ao_entry.dob.strftime('%Y-%m-%d') if ao_entry.dob else None,
                'age': ao_entry.age,
                'nationality': ao_entry.nationality,
                'agent': ao_entry.agent,
                'designation': ao_entry.designation,
                'gender': ao_entry.gender,
                'employee_status': ao_entry.employee_status,
                'grade': ao_entry.grade,
                'basic': float(ao_entry.basic) if ao_entry.basic else None,
                'hra': float(ao_entry.hra) if ao_entry.hra else None,
                'transportation_allowance': float(ao_entry.transportation_allowance) if ao_entry.transportation_allowance else None,
                'accommodation': float(ao_entry.accommodation) if ao_entry.accommodation else None,
                'telephone': float(ao_entry.telephone) if ao_entry.telephone else None,
                'additional_duty_allowance': float(ao_entry.additional_duty_allowance) if ao_entry.additional_duty_allowance else None,
                'other_allowance': float(ao_entry.other_allowance) if ao_entry.other_allowance else None,
                'total': float(ao_entry.total) if ao_entry.total else None,
                'in_words': ao_entry.in_words,
                'ao_acceptance': ao_entry.ao_acceptance,
                'acceptance_date': ao_entry.acceptance_date.strftime('%Y-%m-%d') if ao_entry.acceptance_date else None,
                'document_status': ao_entry.document_status,
                'interview_date': ao_entry.interview_date.strftime('%Y-%m-%d') if ao_entry.interview_date else None
            }
            return JsonResponse(data)
        except Recruitment.DoesNotExist:
            return JsonResponse({'error': 'AO Entry not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def ao_entry_update(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            ao_entry_id = request.POST.get('ao_entry_id')
            ao_entry = Recruitment.objects.get(recr_id=ao_entry_id, comp_code=COMP_CODE)

            # Update fields
            ao_entry.ao_issued_date = request.POST.get('ao_issued_date')
            ao_entry.dep = request.POST.get('dep')
            ao_entry.project = request.POST.get('project')
            ao_entry.mrf = request.POST.get('mrf')
            ao_entry.ao_ref_no = request.POST.get('ao_ref_no')
            ao_entry.category = request.POST.get('category')
            ao_entry.name_as_per_pp = request.POST.get('name_as_per_pp')
            ao_entry.pp_number = request.POST.get('pp_number')
            ao_entry.pp_exp_date = request.POST.get('pp_exp_date') or None
            ao_entry.pp_validity_days = request.POST.get('pp_validity_days')
            ao_entry.dob = request.POST.get('dob') or None
            ao_entry.age = request.POST.get('age')
            ao_entry.nationality = request.POST.get('nationality')
            ao_entry.agent = request.POST.get('agent')
            ao_entry.designation = request.POST.get('designation')
            ao_entry.gender = request.POST.get('gender')
            ao_entry.employee_status = request.POST.get('employee_status')
            ao_entry.grade = request.POST.get('grade')
            ao_entry.basic = request.POST.get('basic')
            ao_entry.hra = request.POST.get('hra')
            ao_entry.transportation_allowance = request.POST.get('transportation_allowance')
            ao_entry.accommodation = request.POST.get('accommodation')
            ao_entry.telephone = request.POST.get('telephone')
            ao_entry.additional_duty_allowance = request.POST.get('additional_duty_allowance')
            ao_entry.other_allowance = request.POST.get('other_allowance')
            ao_entry.total = request.POST.get('total')
            ao_entry.in_words = request.POST.get('in_words')
            ao_entry.ao_acceptance = request.POST.get('ao_acceptance')
            ao_entry.acceptance_date = request.POST.get('acceptance_date') or None
            ao_entry.document_status = request.POST.get('document_status')
            ao_entry.interview_date = request.POST.get('interview_date') or None
            # ao_entry.modified_by = request.user.id
            # ao_entry.modified_on = datetime.now()
            
            ao_entry.save()
            messages.success(request, 'AO Entry updated successfully!')
            return redirect('ao_entry_list')
        except Recruitment.DoesNotExist:
            messages.error(request, 'AO Entry not found!')
            return redirect('ao_entry_list')
        except Exception as e:
            messages.error(request, f'Error updating AO Entry: {str(e)}')
            return redirect('ao_entry_list')
    return redirect('ao_entry_list')

def ao_entry_delete(request, recr_id):
    set_comp_code(request)
    try:
        ao_entry = Recruitment.objects.get(recr_id=recr_id, comp_code=COMP_CODE)
        ao_entry.delete()
        messages.success(request, 'AO Entry deleted successfully!')
    except Recruitment.DoesNotExist:
        messages.error(request, 'AO Entry not found!')
    except Exception as e:
        messages.error(request, f'Error deleting AO Entry: {str(e)}')
    return redirect('ao_entry_list')

def recruitment_list(request):
    keyword = request.GET.get('keyword', '')
    entries = Recruitment.objects.filter(ao_acceptance='Yes').order_by('-ao_issued_date')
    if keyword:
        entries = entries.filter(
            Q(name_as_per_pp__icontains=keyword) |
            Q(ao_ref_no__icontains=keyword) |
            Q(project__icontains=keyword) |
            Q(dep__icontains=keyword)
        )
    paginator = Paginator(entries, 10)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    context = {
        'entries': entries,
        'result_cnt': entries.paginator.count if entries else 0,
        'keyword': keyword
    }
    return render(request, 'pages/payroll/recruitment/recruitment_list.html', context)

@csrf_exempt
def recruitment_edit(request):
    if request.method == 'GET':
        try:
            recruitment_id = request.GET.get('recr_id')
            rec = Recruitment.objects.get(recr_id=recruitment_id)
            data = {
                'recr_id': rec.recr_id,
                'ao_ref_no': rec.ao_ref_no,
                'name_as_per_pp': rec.name_as_per_pp,
                'dep': rec.dep,
                'project': rec.project,
                'designation': rec.designation,
                'nationality': rec.nationality,
                'employee_status': rec.employee_status,
                'gender': rec.gender,
                'agency_name': rec.agency_name,
                'doc_status': rec.doc_status,
                'interview_date': rec.interview_date.strftime('%Y-%m-%d') if rec.interview_date else '',
                # Editable fields:
                'availability': rec.availability,
                'agent_charges': rec.agent_charges,
                'charges_paid_date': rec.charges_paid_date.strftime('%Y-%m-%d') if rec.charges_paid_date else '',
                'pcc_certificate': rec.pcc_certificate,
                'doc_status': rec.doc_status,
                'pre_approval': rec.pre_approval,
                'work_offer_letter': rec.work_offer_letter,
                'insurance': rec.insurance,
                'wp_payment': rec.wp_payment,
                'visa_submission': rec.visa_submission,
                'change_status': rec.change_status,
                'visa_issued_date': rec.visa_issued_date.strftime('%Y-%m-%d') if rec.visa_issued_date else '',
                'arrival_date': rec.arrival_date.strftime('%Y-%m-%d') if rec.arrival_date else '',
                'airport': rec.airport,
                'flight_no': rec.flight_no,
                'eta': rec.eta.strftime('%Y-%m-%dT%H:%M') if rec.eta else '',
                'arrived_or_not': rec.arrived_or_not,
                'convert_to_employee_flag': rec.convert_to_employee_flag
            }
            return JsonResponse(data)
        except Recruitment.DoesNotExist:
            return JsonResponse({'error': 'Recruitment entry not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def recruitment_update(request):
    if request.method == 'POST':
        try:
            recruitment_id = request.POST.get('recr_id')
            rec = Recruitment.objects.get(recr_id=recruitment_id)
            # Only update editable fields
            rec.agency_name = request.POST.get('agency_name')
            rec.availability = request.POST.get('availability')
            rec.agent_charges = request.POST.get('agent_charges') or None
            rec.charges_paid_date = request.POST.get('charges_paid_date') or None
            rec.pcc_certificate = request.POST.get('pcc_certificate')
            rec.doc_status = request.POST.get('doc_status')
            rec.pre_approval = request.POST.get('pre_approval')
            rec.work_offer_letter = request.POST.get('work_offer_letter')
            rec.insurance = request.POST.get('insurance')
            rec.wp_payment = request.POST.get('wp_payment')
            rec.visa_submission = request.POST.get('visa_submission')
            rec.change_status = request.POST.get('change_status')
            rec.visa_issued_date = request.POST.get('visa_issued_date') or None
            rec.arrival_date = request.POST.get('arrival_date') or None
            rec.airport = request.POST.get('airport')
            rec.flight_no = request.POST.get('flight_no')
            rec.eta = request.POST.get('eta') or None
            rec.arrived_or_not = request.POST.get('arrived_or_not')
            rec.save()
            return redirect('recruitment_list')
        except Recruitment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Recruitment entry not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def employee_pp_list(request):
    keyword = request.GET.get('keyword', '')
    entries = EmployeePPDetails.objects.all()
    if keyword:
        entries = entries.filter(
            Q(name__icontains=keyword) |
            Q(pp_number__icontains=keyword) |
            Q(emp_code__icontains=keyword) |
            Q(in_outside__icontains=keyword) |
            Q(status__icontains=keyword) |
            Q(sub_status__icontains=keyword) |
            Q(work_location__icontains=keyword) |
            Q(designation__icontains=keyword) |
            Q(nationality__icontains=keyword) |
            Q(pp_control__icontains=keyword) |
            Q(no_of_days__icontains=keyword) |
            Q(medical__icontains=keyword) |
            Q(medical_result_date__icontains=keyword) |
            Q(remedical_result_date__icontains=keyword) |
            Q(eid__icontains=keyword) |
            Q(rp_stamping__icontains=keyword) |
            Q(fine_amount__icontains=keyword) |
            Q(tawjeeh_payment__icontains=keyword) |
            Q(tawjeeh_class__icontains=keyword) |
            Q(iloe_status__icontains=keyword)
        )
    paginator = Paginator(entries, 10)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    context = {
        'entries': entries,
        'result_cnt': entries.paginator.count if entries else 0,
        'keyword': keyword
    }
    return render(request, 'pages/payroll/employee_pp/employee_pp_list.html', context)

def employee_pp_create(request):
    if request.method == 'POST':
        # Create new record
        EmployeePPDetails.objects.create(
            pp_number=request.POST.get('pp_number'),
            emp_code=request.POST.get('emp_code'),
            name=request.POST.get('name'),
            in_outside=request.POST.get('in_outside'),
            status=request.POST.get('status'),
            sub_status=request.POST.get('sub_status'),
            work_location=request.POST.get('work_location'),
            doj=request.POST.get('doj') or None,
            gender=request.POST.get('gender'),
            designation=request.POST.get('designation'),
            nationality=request.POST.get('nationality'),
            pp_control=request.POST.get('pp_control'),
            date_of_landing=request.POST.get('date_of_landing') or None,
            no_of_days=request.POST.get('no_of_days') or None,
            medical=request.POST.get('medical'),
            medical_result_date=request.POST.get('medical_result_date') or None,
            remedical_result_date=request.POST.get('remedical_result_date') or None,
            eid=request.POST.get('eid'),
            rp_stamping=request.POST.get('rp_stamping'),
            fine_amount=request.POST.get('fine_amount') or None,
            tawjeeh_payment=request.POST.get('tawjeeh_payment') or None,
            tawjeeh_class=request.POST.get('tawjeeh_class'),
            iloe_status=request.POST.get('iloe_status'),
        )
        return redirect('employee_pp_list')
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def employee_pp_edit(request):
    # Return JSON for the given id
    id = request.GET.get('id')
    try:
        obj = EmployeePPDetails.objects.get(id=id)
        data = {
            'id': obj.id,
            'pp_number': obj.pp_number,
            'emp_code': obj.emp_code,
            'name': obj.name,
            'in_outside': obj.in_outside,
            'status': obj.status,
            'sub_status': obj.sub_status,
            'work_location': obj.work_location,
            'doj': obj.doj,
            'gender': obj.gender,
            'designation': obj.designation,
            'nationality': obj.nationality,
            'pp_control': obj.pp_control,
            'date_of_landing': obj.date_of_landing,
            'no_of_days': obj.no_of_days,
            'medical': obj.medical,
            'medical_result_date': obj.medical_result_date,
            'remedical_result_date': obj.remedical_result_date,
            'eid': obj.eid,
            'rp_stamping': obj.rp_stamping,
            'fine_amount': obj.fine_amount,
            'tawjeeh_payment': obj.tawjeeh_payment,
            'tawjeeh_class': obj.tawjeeh_class,
            'iloe_status': obj.iloe_status,
        }
        # Convert dates to string if needed
        for k in ['doj', 'medical_result_date', 'remedical_result_date']:
            if data[k]:
                data[k] = data[k].strftime('%Y-%m-%d')
        return JsonResponse(data)
    except EmployeePPDetails.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Not found'})

@csrf_exempt
def employee_pp_update(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            obj = EmployeePPDetails.objects.get(id=id)
            obj.pp_number = request.POST.get('pp_number')
            obj.emp_code = request.POST.get('emp_code')
            obj.name = request.POST.get('name')
            obj.in_outside = request.POST.get('in_outside')
            obj.status = request.POST.get('status')
            obj.sub_status = request.POST.get('sub_status')
            obj.work_location = request.POST.get('work_location')
            obj.doj = request.POST.get('doj') or None
            obj.gender = request.POST.get('gender')
            obj.designation = request.POST.get('designation')
            obj.nationality = request.POST.get('nationality')
            obj.pp_control = request.POST.get('pp_control')
            obj.date_of_landing = request.POST.get('date_of_landing') or None
            obj.no_of_days = request.POST.get('no_of_days') or None
            obj.medical = request.POST.get('medical')
            obj.medical_result_date = request.POST.get('medical_result_date') or None
            obj.remedical_result_date = request.POST.get('remedical_result_date') or None
            obj.eid = request.POST.get('eid')
            obj.rp_stamping = request.POST.get('rp_stamping')
            obj.fine_amount = request.POST.get('fine_amount') or None
            obj.tawjeeh_payment = request.POST.get('tawjeeh_payment') or None
            obj.tawjeeh_class = request.POST.get('tawjeeh_class')
            obj.iloe_status = request.POST.get('iloe_status')
            obj.save()
            return redirect('employee_pp_list')
        except EmployeePPDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@csrf_exempt
def employee_pp_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            obj = EmployeePPDetails.objects.get(id=id)
            obj.delete()
            return JsonResponse({'status': 'success'})
        except EmployeePPDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@csrf_exempt
def get_employee_details_by_code(request):
    emp_code = request.GET.get('emp_code')
    try:
        from .models import Employee
        emp = Employee.objects.get(emp_code=emp_code)
        data = {
            'pp_number': emp.passport_details or '',
            'name': emp.emp_name or '',
            'in_outside': emp.visa_location or '',
            'status': emp.emp_status or '',
            'sub_status': emp.emp_sub_status or '',
            'work_location': emp.select_camp or '',
            'doj': emp.date_of_join.strftime('%Y-%m-%d') if emp.date_of_join else '',
            'gender': emp.emp_sex or '',
            'designation': emp.designation or '',
            'nationality': emp.nationality or '',
        }
        return JsonResponse({'success': True, 'data': data})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'})

@csrf_exempt
def check_leave_exists(request):
    if request.method == 'GET':
        try:
            employee_code = request.GET.get('employee_code')
            leave_type = request.GET.get('leave_type')
            year = request.GET.get('year')
            
            # Get all approved leaves for this employee and leave type in the current year
            from .models import LeaveTransaction
            from django.db.models import Sum
            
            # Get the start and end dates for the year
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            # Query for approved leaves
            taken_leaves = LeaveTransaction.objects.filter(
                employee=employee_code,
                leave_type=leave_type,
                start_date__gte=start_date,
                end_date__lte=end_date,
                hr_status='Approved'  # Only count approved leaves
            ).aggregate(total_days=Sum('total_leave_days'))
            
            # Get the total days taken (default to 0 if none found)
            taken_days = taken_leaves['total_days'] or 0
            
            return JsonResponse({
                'status': 'success',
                'taken_days': taken_days
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


@csrf_exempt
def recruitment_update(request):
    if request.method == 'POST':
        try:
            recruitment_id = request.POST.get('recr_id')
            rec = Recruitment.objects.get(recr_id=recruitment_id)
            # Only update editable fields
            rec.interview_date = request.POST.get('interview_date') or None
            rec.agency_name = request.POST.get('agency_name')
            rec.availability = request.POST.get('availability')
            rec.agent_charges = request.POST.get('agent_charges') or None
            rec.charges_paid_date = request.POST.get('charges_paid_date') or None
            rec.pcc_certificate = request.POST.get('pcc_certificate')
            rec.doc_status = request.POST.get('doc_status')
            rec.pre_approval = request.POST.get('pre_approval')
            rec.work_offer_letter = request.POST.get('work_offer_letter')
            rec.insurance = request.POST.get('insurance')
            rec.wp_payment = request.POST.get('wp_payment')
            rec.visa_submission = request.POST.get('visa_submission')
            rec.change_status = request.POST.get('change_status')
            rec.visa_issued_date = request.POST.get('visa_issued_date') or None
            rec.arrival_date = request.POST.get('arrival_date') or None
            rec.airport = request.POST.get('airport')
            rec.flight_no = request.POST.get('flight_no')
            rec.eta = request.POST.get('eta') or None
            rec.arrived_or_not = request.POST.get('arrived_or_not')
            rec.save()
            return redirect('recruitment_list')
        except Recruitment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Recruitment entry not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def convert_to_employee(request):
    if request.method == 'POST':
        try:
            recr_id = request.POST.get('recr_id')
            rec = Recruitment.objects.get(recr_id=recr_id)
            # Only update editable fields
            rec.interview_date = request.POST.get('interview_date') or None
            rec.agency_name = request.POST.get('agency_name')
            rec.availability = request.POST.get('availability')
            rec.agent_charges = request.POST.get('agent_charges') or None
            rec.charges_paid_date = request.POST.get('charges_paid_date') or None
            rec.pcc_certificate = request.POST.get('pcc_certificate')
            rec.doc_status = request.POST.get('doc_status')
            rec.pre_approval = request.POST.get('pre_approval')
            rec.work_offer_letter = request.POST.get('work_offer_letter')
            rec.insurance = request.POST.get('insurance')
            rec.wp_payment = request.POST.get('wp_payment')
            rec.visa_submission = request.POST.get('visa_submission')
            rec.change_status = request.POST.get('change_status')
            rec.visa_issued_date = request.POST.get('visa_issued_date') or None
            rec.arrival_date = request.POST.get('arrival_date') or None
            rec.airport = request.POST.get('airport')
            rec.flight_no = request.POST.get('flight_no')
            rec.eta = request.POST.get('eta') or None
            rec.arrived_or_not = request.POST.get('arrived_or_not')
            rec.convert_to_employee_flag = 'Y'
            rec.save()
            with connection.cursor() as cursor:
                cursor.execute("CALL insert_employee_and_allowances_by_recr_id(%s)", [recr_id])
                messages.success(request, 'Successfully converted to employee!')
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def mrf_list(request):
    set_comp_code(request)
    """View to list all MRFs"""
    keyword = request.GET.get('keyword', '')
    
    # Get all MRFs
    mrfs = MRFMaster.objects.filter(comp_code = COMP_CODE)
    
    # Apply search filter if keyword exists
    if keyword:
        mrfs = mrfs.filter(
            Q(mrf_number__icontains=keyword) |
            Q(project_code__icontains=keyword) |
            Q(designation_code__icontains=keyword)
        )
    
    # Get projects for dropdown
    projects = projectMaster.objects.filter(comp_code=COMP_CODE, is_active=True)
    
    # Get designations for dropdown
    designations = CodeMaster.objects.filter(
        comp_code=COMP_CODE,
        base_type='DESIGNATION',
        is_active='Y'
    )
    
    
    context = {
        'mrfs': mrfs,
        'projects': projects,
        'designations': designations,
        'keyword': keyword,
        'result_cnt': mrfs.count()
    }
    
    return render(request, 'pages/payroll/mrf/mrf.html', context)

@csrf_exempt
def create_mrf(request):
    """View to create a new MRF"""
    if request.method == 'POST':
        try:
            # Generate MRF number
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'MRF'])
                    result = cursor.fetchone()
                    mrf_number = result[0] if result else None
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
            
            # Create new MRF
            mrf = MRFMaster.objects.create(
                mrf_number=mrf_number,
                comp_code=COMP_CODE,
                project_code=request.POST.get('project_code'),
                designation_code=request.POST.get('designation_code'),
                category=request.POST.get('category'),
                quantity=request.POST.get('quantity'),
                remaining_quantity=request.POST.get('quantity'),
                status='Open',
                remarks=request.POST.get('remarks'),
                created_by=request.user.username,
                updated_by=request.user.username
            )
            
            return redirect('mrf_list')
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def edit_mrf(request):
    set_comp_code(request)
    """View to edit an existing MRF"""
    if request.method == 'POST':
        try:
            mrf_id = request.POST.get('mrf_id')
            mrf = MRFMaster.objects.get(id=mrf_id, comp_code=COMP_CODE)
            mrf.remaining_quantity = request.POST.get('remaining_quantity')
            mrf.category = request.POST.get('category')
            mrf.status = request.POST.get('status')
            mrf.remarks = request.POST.get('remarks')
            mrf.updated_by = request.user.username
            mrf.save()
            
            return redirect('mrf_list')
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_mrf(request):
    set_comp_code(request)
    """View to delete an MRF"""
    if request.method == 'POST':
        try:
            mrf_id = request.POST.get('mrf_id')
            mrf = MRFMaster.objects.get(id=mrf_id, comp_code=COMP_CODE)
            mrf.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'MRF deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def get_mrf_details(request):
    set_comp_code(request)
    """View to get MRF details for editing"""
    try:
        mrf_id = request.GET.get('mrf_id')
        mrf = MRFMaster.objects.get(id=mrf_id, comp_code=COMP_CODE)
        
        data = {
            'project_code': mrf.project_code,
            'designation_code': mrf.designation_code,
            'category': mrf.category,
            'quantity': mrf.quantity,
            'remaining_quantity': mrf.remaining_quantity,
            'status': mrf.status,
            'remarks': mrf.remarks
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)