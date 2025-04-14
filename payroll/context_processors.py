# your_app/context_processors.py

from .models import CodeMaster, GradeMaster, Employee, projectMaster,PaycycleMaster
from django.http import  JsonResponse
from .views import set_comp_code

def get_comp_code(request):
    global PAY_CYCLES
    pay_cycles_raw = request.session.get("user_paycycles", "")

    # Split pay cycles by ":" if it's a string, default to empty list
    PAY_CYCLES = pay_cycles_raw.split(":") if isinstance(pay_cycles_raw, str) else []
    return request.session.get('comp_code')

def gender_data(request):
    comp_code = get_comp_code(request)
    set_comp_code(request)
    gender_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='SEX')
    return {
        'gender_data': gender_data
    }

def get_paycycle(request):
    comp_code = get_comp_code(request)
    paycycle_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='PROCESS CYCLE')
    paymonth = PaycycleMaster.objects.filter(comp_code=comp_code)
    return {
        'paycycle_data': paycycle_data,
        'paymonth': paymonth  
    }

def get_country(request):
    comp_code = get_comp_code(request)
    country_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='COUNTRY')
    return {
        'country_data': country_data
    }

def get_place(request):
    comp_code = get_comp_code(request)
    place_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='PLACE')
    return {
        'place_data': place_data
    }

def get_bank(request):
    comp_code = get_comp_code(request)
    bank_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='BANK')
    return {
        'bank_data': bank_data
    }

def get_branch(request):
    comp_code = get_comp_code(request)
    branch_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='BRANCH')
    return {
        'branch_data': branch_data
    }

def get_documents(request):
    comp_code = get_comp_code(request)
    doc_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='DOC')
    return {
        'doc_data': doc_data
    }

def check_process_cycle(request):
    if request.method == 'POST':
        process_cycle = request.POST.get('process_cycle')
        comp_code = get_comp_code(request)
        exists = CodeMaster.objects.filter(comp_code=comp_code, base_type='PROCESS CYCLE', base_value=process_cycle).exists()
        return JsonResponse({'exists': exists})

def get_pay_process_flag(request):
    comp_code = get_comp_code(request)
    pay_flag_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='PROCESS COMPLETION FLAG')
    return {   
        'pay_flag_data': pay_flag_data
        }

def get_status(request):
    comp_code = get_comp_code(request)
    status_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='STATUS')
    return {
        'status_data': status_data
        }

def mar_status(request):
    comp_code = get_comp_code(request)
    mar_status_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='MARITAL STATUS')
    return {
         'mar_status_data': mar_status_data
         }

def desig(request):
    comp_code = get_comp_code(request)
    desig_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='DESIGNATION')
    return {
         'desig_data': desig_data
         }

def dept(request):
    comp_code = get_comp_code(request)
    dept_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='DEPT')
    return {
         'dept_data': dept_data
         }

def process_flag(request):
    comp_code = get_comp_code(request)
    pf_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='PROCESS COMPLETION FLAG')
    return {
         'pf_data': pf_data
         }

def at_uom(request):
    comp_code = get_comp_code(request)
    at_uom_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='ATTENDANCE UOM')
    return {
         'at_uom_data': at_uom_data
         }

def pro_type(request):
    comp_code = get_comp_code(request)
    pro_type_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='PROJECT TYPE')
    return {
         'pro_type_data': pro_type_data
         }

def pro_city(request):
    comp_code = get_comp_code(request)
    pro_city_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='PROJECT CITY')
    return {
         'pro_city_data': pro_city_data
         }

def nationality(request):
    comp_code = get_comp_code(request)
    nation_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='NATIONALITY')
    return {
         'nation_data': nation_data
         }

def hol_type(request):
    comp_code = get_comp_code(request)
    hol_type_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='HOLIDAY')
    return {
         'hol_type_data': hol_type_data
         }

def grade_code(request):
    comp_code = get_comp_code(request)
    grade_code_data = GradeMaster.objects.filter(comp_code=comp_code, is_active = 'Y')
    return {
        'grade_code_data': grade_code_data
        }

def project(request):
    comp_code = get_comp_code(request)
    project_data = projectMaster.objects.filter(comp_code=comp_code, is_active= True)
    return {
        'project_data': project_data
        }

def employee(request):
    comp_code = get_comp_code(request)
    employee_data = Employee.objects.filter(comp_code=comp_code, process_cycle__in = PAY_CYCLES)
    return {
        'employee_data': employee_data
        }

def get_earnings(requests):
    comp_code = get_comp_code(requests)
    earnings_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'EARNINGS')
    return {
        'earnings_data': earnings_data
        }

def get_deductions(requests):
    comp_code = get_comp_code(requests)
    deductions_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'DEDUCTION')
    return {
        'deductions_data': deductions_data
        }

def get_relatives(request):
    comp_code = get_comp_code(request)
    relatives_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'RELATIVES')
    return {
        'relatives_data': relatives_data
        }

def get_other_documents(request):
    comp_code = get_comp_code(request)
    other_documents_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'OTHER_DOCUMENTS')
    return {
        'other_documents_data': other_documents_data
        }

def get_emirates(request):
    comp_code = get_comp_code(request)
    emirates_list = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'EMIRATES')
    return {
        'emirates_list': emirates_list
        }

def get_nationality(request):
    comp_code = get_comp_code(request)
    nationality_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'NATIONALITY')
    return {
        'nationality_data': nationality_data
        }

def get_work_location(request):
    comp_code = get_comp_code(request)
    work_location_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'WORK_LOCATION')
    return {
        'work_location_data': work_location_data
        }

def get_service_type(request):
    comp_code = get_comp_code(request)
    service_type_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'SERVICE_TYPE')
    return {
        'service_type_data': service_type_data
        }

def get_service_category(request):
    comp_code = get_comp_code(request)
    service_category_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'SERVICE_CATEGORY')
    return {
        'service_category_data': service_category_data
        }

def get_pro_sub_location(request):
    comp_code = get_comp_code(request)
    pro_sub_location_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'PROJECT_SUB_LOCATION')
    return {
        'pro_sub_location_data': pro_sub_location_data
        }


def get_project_status(request):
    comp_code = get_comp_code(request)
    project_status_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'PROJECT_STATUS')
    return {
        'project_status_data': project_status_data
        }

