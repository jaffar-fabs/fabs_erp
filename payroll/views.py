from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import uuid
from datetime import datetime

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
)

from .models import Menu, RoleMenu, Employee


def employee_master(request):
    # Fetch all employee data for display
    employee_data = Employee.objects.all()
    return render(request, 'pages/payroll/employee_master/employee_master.html', {'employees': employee_data})

def save_employee(request, employee_id=None):
    if request.method == "POST":
        
        if employee_id:
            employee = get_object_or_404(Employee, employee_id=employee_id)
        else:  
            employee = Employee()  

        # Common fields to extract
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
        employee.res_country_code = request.POST.get("res_country_code") or None
        employee.res_phone_no = request.POST.get("res_phone_no") or None
        employee.res_addr_line1 = request.POST.get("res_addr_line1")
        employee.res_addr_line2 = request.POST.get("res_addr_line2")
        employee.res_city = request.POST.get("res_city")
        employee.res_state = request.POST.get("res_state")
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
        employee.bank_loan = request.POST.get("bank_loan")
        # employee.is_active = True
        # Travel Document Details
        employee.passport_document = request.FILES.get("passport_document")  # Handle file upload
        employee.passport_details = request.POST.get("passport_details")
        employee.issued_date = request.POST.get("issued_date") or None
        employee.expiry_date = request.POST.get("expiry_date") or None

        # Handle Visa Details
        employee.visa_no = request.POST.get("visa_no")
        employee.visa_issued = request.POST.get("visa_issued") or None
        employee.visa_expiry = request.POST.get("visa_expiry") or None
        employee.emirate_issued = request.POST.get("emirate_issued") or None
        employee.emirate_expiry = request.POST.get("emirate_expiry") or None
        employee.uid_number = request.POST.get("uid_number")
        employee.mohra_number = request.POST.get("mohra_number")
        employee.work_permit_number = request.POST.get("work_permit_number")
        employee.work_permit_expiry = request.POST.get("work_permit_expiry") or None
        employee.visa_document = request.FILES.get("visa_document")  # Handle visa document upload
        employee.emirate_document = request.FILES.get("emirate_document")  # Handle emirate document upload
        employee.work_permit_document = request.FILES.get("work_permit_document")  # Handle work permit document upload


        employee.created_by = 1 
        employee.modified_by = 1
        employee.created_on = request.POST.get("created_on") or None
        employee.modified_on = request.POST.get("modified_on") or None

        employee.save()

        return redirect('/employee') 
    employee_data = Employee.objects.all()
    return render(request, 'pages/payroll/employee_master/employeemaster.html', {'employees': employee_data})

def deactivate_employee(request, employee_id):
    if request.method == 'POST':
        # Get the Employee object
        employee = get_object_or_404(Employee, employee_id=employee_id)
        # Update is_active to False
        employee.emp_status = 'inactive'
        employee.save()
        messages.success(request, 'Employee deactivated successfully!')
    return redirect('/employee')  # Redirect to the employee list page

def index(request):
    deals_dashboard = [
        {
            "id" : 1,
            "deal_name" : "Collins",
            "stage" : "Conversation",
            "deal_value" : "$04,51,000",
            "probability" : "85%",
            "status" : "Lost"
        },
        {
            "id" : 2,
            "deal_name" : "Konopelski",
            "stage" : "Pipeline",
            "deal_value" : "$14,51,000",
            "probability" : "56%",
            "status" : "Won"
        },
        {
            "id" : 3,
            "deal_name" : "Adams",
            "stage" : "Won",
            "deal_value" : "$12,51,000",
            "probability" : "15%",
            "status" : "Won"
        },
        {
            "id" : 4,
            "deal_name" : "Schumm",
            "stage" : "Lost",
            "deal_value" : "$51,000",
            "probability" : "45%",
            "status" : "Lost"
        },
        {
            "id" : 5,
            "deal_name" : "Wisozk",
            "stage" : "Follow Up",
            "deal_value" : "$67,000",
            "probability" : "5%",
            "status" : "Won"
        }
    ]
    return render(request, 'pages/dashboard/index.html', {'deals_dashboard': deals_dashboard})

def my_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = UserMaster.objects.get(user_id=username, is_active=True)

            if password == user.password:  
                request.session["username"] = user.user_id
                request.session["role"] = "Administrator" if user.user_id == "admin1" else "Programmer"
                request.session["role_id"] = 1 if user.user_id == "admin1" else 2
                
                messages.success(request, "Login successful!")
                return redirect("/index")
            else:
                messages.error(request, "Invalid username or password.")
        except UserMaster.DoesNotExist:
            messages.error(request, "Invalid username or password.")

    return render(request, "auth/login.html")

def dashboard_view(request):
    try:
        role_id = request.session.get("role_id")
        menu_ids = RoleMenu.objects.filter(role_id=role_id, view = True).values_list('menu_id', flat=True)
        parent_menu_data = list(Menu.objects.filter(menu_id__in=menu_ids, parent_menu_id__isnull=True).order_by('display_order').values('menu_id', 'screen_name'))
        child_menu_data = list(Menu.objects.filter(menu_id__in=menu_ids, parent_menu_id__isnull=False, parent_menu_id__in=menu_ids).order_by('display_order').values('menu_id', 'screen_name', 'url','parent_menu_id'))
        response_data = {'status': 'success', 'parent_menu_data': parent_menu_data, 'child_menu_data': child_menu_data }
    except Exception as e:
        response_data = {'status': 'error', 'msg': str(e)}

    return JsonResponse(response_data)

    
def logout(request):
    request.session.flush()  # Clears all session data
    messages.success(request, "You have been logged out successfully.")
    return redirect("/")  # Redirect to login page

#-------------------------------

#Seed Master View

def create_seed(request):
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
            comp_code="1000",
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

    seed_data = SeedModel.objects.all()
    return render(request, 'pages/payroll/seed_master/seedmaster.html', {'seed_data': seed_data})

def update_seed_status(request, seed_id):
    if request.method == 'POST':
        seed = get_object_or_404(SeedModel, seed_id=seed_id)
        seed.is_active = False
        seed.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def edit_seed(request, seed_id):
    seed = get_object_or_404(SeedModel, seed_id=seed_id)

    if request.method == 'POST':
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
        
        # Ensure the status is correctly updated based on the form submission
        if 'status' in request.POST:
            seed.is_active = request.POST.get('status') == 'active'
        
        seed.modified_by = 1

        seed.save()
        return redirect('create_seed')
    else:
        return render(request, 'pages/modal/payroll/seed-modal.html', {'seed': seed})

def get_seed(request, seed_id):
    seed = SeedModel.objects.get(seed_id=seed_id)
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
    return JsonResponse(data)


#--------------------------------------------------


class Paycycle(View):
    template_name = "pages/payroll/paycycle_master/paycycle-list.html"

    def get(self, request):
        paycycle_list = PaycycleMaster.objects.all().order_by('-created_on')
        return render(request, self.template_name, {"paycycle_list": paycycle_list})

    def post(self, request):
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
            paycycle = get_object_or_404(PaycycleMaster, process_cycle_id=process_cycle_id)
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
                comp_code='1000',
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
        paycycle = get_object_or_404(PaycycleMaster, process_cycle_id=process_cycle_id)
        paycycle.is_active = "N"
        paycycle.save()
        return JsonResponse({"status": "success", "message": "Paycycle deactivated successfully."})


    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def get_next_process_cycle_id(self):
        auto_paycycle_id = PaycycleMaster.objects.filter(comp_code='1000').order_by('-process_cycle_id').first()
        return auto_paycycle_id.process_cycle_id + 1 if auto_paycycle_id else 1
    
    



def project(request):
    template_name = 'pages/payroll/project_master/projects.html'

   
    if request.method == "GET":
        project_id = request.GET.get("project_id")


      
            

        try:
            project = get_object_or_404(projectMatster, project_id=int(project_id))
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
                # "prj_city":project.prj_city
                "prj_city":project.prj_city
            })
        
        except Exception as e:
            print(f" Error project Edit: {str(e)}")  
        
    
    if request.method == "POST":
        
            project_id = request.POST.get("project_id")
            if projectMatster.objects.filter(project_id=project_id).exists():
                project = get_object_or_404(projectMatster, project_id=int(project_id))

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
                comp_code=request.POST.get("comp_code", "1000"),
                )
                project.save()
            return redirect("project")


    # projects = projectMatster.objects.filter(is_active=True).order_by('-created_on')
    projects = projectMatster.objects.all().order_by('-created_on')
    project_count=projectMatster.objects.all()
    # print("COUNT ",project_count)
    return render(request, template_name, {'projects': projects,'project_count':project_count})


def check_project_code(request):
    """API to check if project code already exists."""
    if request.method == "POST":
        project_code = request.POST.get("project_code")

        if projectMatster.objects.filter(prj_code=project_code).exists():
            return JsonResponse({"exists": True})  # Project code exists
        else:
            return JsonResponse({"exists": False})  # Project code is unique

    return JsonResponse({"error": "Invalid request"}, status=400)


def delete_project(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")

        if project_id:
            project = get_object_or_404(projectMatster, project_id=project_id)
            project.is_active = False  
            project.save()
    return redirect("project")

# Holiday Master -------------------------

# class HolidayMaster(View):






from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from .models import CodeMaster

class CodeMasterList(View):

    template_name = "pages/payroll/code_master/code_master_list.html"

    def get(self, request): 
        base_type_suggestions = CodeMaster.objects.filter(comp_code="999").values("base_description", "base_value").distinct()
        base_type_comp_code = CodeMaster.objects.filter(comp_code="999").values("base_value", "base_description").distinct()
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
        if CodeMaster.objects.filter(base_type=base_type, base_value=base_value, comp_code="1000").exists():
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
            code_master = CodeMaster.objects.filter(base_type=base_code, base_value=base_value, comp_code="1000").first()
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
            base_values = CodeMaster.objects.filter(base_type=base_code, comp_code="1000").values("base_value", "is_active")
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
            existing_entry = CodeMaster.objects.filter(comp_code="1000", base_type=base_type, base_value=base_value).exists()
            if not existing_entry:
                CodeMaster.objects.create(
                    comp_code="1000",
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
            base_description_obj = CodeMaster.objects.filter(base_type=base_code, base_value=base_value, comp_code="1000").values("base_description", "is_active").first()
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
            code_master = CodeMaster.objects.filter(base_type=base_code, base_value=base_value, comp_code="1000").first()
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
        return render(request, self.template_name)

class UserMasterList(View):
    template_name = 'pages/payroll/user/user_master.html'

    def get(self, request):
        users = UserMaster.objects.all()
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
            if UserMaster.objects.filter(user_id=user_id).exists():
                return JsonResponse({'status': 'error', 'field': 'user_id', 'message': 'User ID already exists.'})
            return JsonResponse({'status': 'success', 'message': 'User ID is available.'})

        if UserMaster.objects.filter(user_id=user_id).exists():
            return JsonResponse({'status': 'error', 'field': 'user_id', 'message': 'User ID already exists.'})

        try:
            user = UserMaster(
                comp_code=1000,
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
            user = get_object_or_404(UserMaster, user_master_id=user_master_id)
    
            user.comp_code = request.POST.get('comp_code')
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
        
        user = get_object_or_404(UserMaster, user_master_id=user_master_id)
        
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
        datas = GradeMaster.objects.filter(comp_code="1000")
        return render(request, self.template_name, {'datas': datas})

    def post(self, request):
        # Check for delete request
        if "delete_grade_id" in request.POST:
            grade_id = request.POST.get("delete_grade_id")
            comp_code = request.POST.get("delete_comp_code")
            GradeMaster.objects.filter(grade_id=grade_id, comp_code=comp_code).update(is_active="N")
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

        if grade_id:
            grade = get_object_or_404(GradeMaster, grade_id=grade_id, comp_code="1000")
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
            grade.modified_by = 1
            grade.modified_on = now()
            grade.save()
        else:
            grade = GradeMaster.objects.create(
                comp_code='1000',
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
            )
            for key, value in allowances.items():
                setattr(grade, key, value)
            grade.save()

        return redirect("grade_master")


# HOLIDAY ---------------------------------  HOLIDAY ----------------------------------------

def holidayList( request):
    template_name="pages/payroll/holiday_master/holiday_list.html"
    holidays_list=HolidayMaster.objects.all().order_by('-created_on')
    holiday_type=CodeMaster.objects.filter(comp_code="1000",base_type ='HOLIDAY');
    print(holiday_type,"Type")
    return render(request,template_name, {'holidays':holidays_list,'holidayTypes':holiday_type})
        

def holidayCreate(request):

    if request.method == "POST":
        # holiDay=request.POST.get("holiday");
        # holiday_date=request.get("holiday_date");
        # if HolidayMaster.objects.filter(holiday=holiDay,holiday_date=holiday_date).exists():
            
        holiday = HolidayMaster(
            comp_code=request.POST.get("comp_code", "1000"),
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
    if request.method == "GET":
        uniqe_id = request.GET.get("holiday_id")
    try:
            holiday = get_object_or_404(HolidayMaster, unique_id=int(uniqe_id))
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
            if HolidayMaster.objects.filter(unique_id=holiday_id).exists():
                holiday = get_object_or_404(HolidayMaster, unique_id=int(holiday_id))
                holiday.holiday = request.POST.get("holiday", holiday.holiday)
                holiday.holiday_date = request.POST.get("holiday_date", holiday.holiday_date)
                holiday.holiday_day = request.POST.get("holiday_day", holiday.holiday_day)
                holiday.holiday_type = request.POST.get("holiday_type", holiday.holiday_type)
                holiday.holiday_description = request.POST.get("holiday_description", holiday.holiday_description)
                holiday.created_by = 1;
                holiday.comp_code = 1000;
                holiday.is_active = request.POST.get("is_active") == "Active"
                holiday.save()
                return redirect("holiday_master")




class MenuMaster(View):
    template_name = "pages/security/menu_master/menu_list.html"

    def get(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            menu_name = request.GET.get('menu_name', None)
            exists = Menu.objects.filter(menu_name=menu_name).exists()
            return JsonResponse({'exists': exists})

        menu_list = Menu.objects.all()
        parent_menus = Menu.objects.values_list('menu_name', flat=True).distinct()
        return render(request, self.template_name, {"menu_list": menu_list, "parent_menus": parent_menus})
    
    def post(self, request):
        menu_id = request.POST.get('menu_id')
        menu_name = request.POST.get('menu_name')
        quick_path = request.POST.get('quick_path')
        screen_name = request.POST.get('screen_name')
        url = request.POST.get('url')
        module_id = request.POST.get('module_id')
        parent_menu_id = request.POST.get('parent_menu_id')
        display_order = request.POST.get('display_order')
        instance_id = request.POST.get('instance_id')
        buffer1 = request.POST.get('buffer1')
        buffer2 = request.POST.get('buffer2')
        buffer3 = request.POST.get('buffer3')
        is_active = True if "is_active" in request.POST else False
        is_add = True if "is_add" in request.POST else False
        is_view = True if "is_view" in request.POST else False
        is_edit = True if "is_edit" in request.POST else False
        is_delete = True if "is_delete" in request.POST else False
        is_execute = True if "is_execute" in request.POST else False
        app_id = request.POST.get('app_id')
        icon = request.POST.get('icon')

        if menu_id:
            menu = get_object_or_404(Menu, menu_id=menu_id)
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
        else:
            Menu.objects.create(
                comp_code="1001",
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

        return redirect("menu_list")


def permission_view(request):
    role_name = request.GET.get('role_name', 'No role name provided')
    # Filter active menu items
    active_menus = Menu.objects.filter(is_active=True)
    context = {
        'role_name': role_name,
        'active_menus': active_menus,
    }
    return render(request, 'pages/security/role/permission.html', context)
