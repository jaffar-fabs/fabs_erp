# your_app/context_processors.py

from .models import *
from procurement.models import *
from django.http import  JsonResponse
from .views import set_comp_code

def get_comp_code(request):
    global PAY_CYCLES
    pay_cycles_raw = request.session.get("user_paycycles", "")

    # Split pay cycles by ":" if it's a string, default to empty list
    PAY_CYCLES = pay_cycles_raw.split(":") if isinstance(pay_cycles_raw, str) else []
    return request.session.get('comp_code')

def get_currency(request):
    comp_code = get_comp_code(request)
    currency_data = CodeMaster.objects.filter(comp_code=comp_code, base_type='CURRENCY')
    return {
        'currency_data': currency_data
    }

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
    employee_data = Employee.objects.filter(comp_code=comp_code, staff_category__in = PAY_CYCLES).order_by('emp_code')
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

def get_company_documents(request):
    comp_code = get_comp_code(request)
    company_documents_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'COMPANY_DOCUMENTS')
    return {
        'comp_doc_data': company_documents_data
        }

def get_floor(request):
    comp_code = get_comp_code(request)
    floor_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'FLOOR')
    return {
        'floor_data': floor_data
        }

def get_room_type(request):
    comp_code = get_comp_code(request)
    room_type_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'ROOM_TYPE')
    return {
        'room_type_data': room_type_data
        }


def get_camp(request):
    comp_code = get_comp_code(request)
    camp_data = CampMaster.objects.filter(comp_code=comp_code)
    return {
        'camp_data': camp_data
        }


def get_customer(request):
    comp_code = get_comp_code(request)
    customer_data = PartyMaster.objects.filter(comp_code=comp_code)
    return{
        'customer_data' : customer_data
    }

def get_uom(request):
    comp_code = get_comp_code(request)
    uom_data = UOMMaster.objects.filter(comp_code=comp_code)
    return {
        'uom_data': uom_data
    }

def get_pr_items(request):
    comp_code = get_comp_code(request)
    
    # Get all PR numbers that are already referenced in POs
    used_pr_numbers = PurchaseOrderHeader.objects.filter(
        comp_code=comp_code,
        refn_numb__isnull=False
    ).values_list('refn_numb', flat=True).distinct()
    
    # Get PR items excluding those that are already used in POs
    pr_items_data = MaterialRequestHeader.objects.filter(
        comp_code=comp_code,
        ordr_type='PR'
    ).exclude(
        ordr_numb__in=used_pr_numbers
    ).order_by('-ordr_date')
    
    return {
        'pr_items_data': pr_items_data
    }

def get_item_categories(request):
    comp_code = get_comp_code(request)
    item_category_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type='ITEM_CATEGORY')
    return {
        'item_category_data': item_category_data
    }

def get_item_sub_categories(request):
    comp_code = get_comp_code(request)
    item_sub_category_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type='ITEM_SUB_CATEGORY')
    return {
        'item_sub_category_data': item_sub_category_data
    }

def get_warehouse_types(request):
    comp_code = get_comp_code(request)
    warehouse_type_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type='WARE_TYPE')
    return {
        'warehouse_type_data': warehouse_type_data
    }

def get_party_type(request):
    comp_code = get_comp_code(request)
    party_type_data = CodeMaster.objects.filter(
        comp_code=comp_code,
        base_type='PARTY_TYPE',
        is_active='Y'
    ).order_by('sequence_id')
    return {
        'party_type_data': party_type_data
    }


def get_leave_types(request):
    comp_code = get_comp_code(request)
    leave_types_data = CodeMaster.objects.filter(
        comp_code=comp_code,
        base_type='LEAVE_TYPES',
        is_active='Y'
    )    
    return {
        'leave_types': leave_types_data
    }

def get_agent(request):
    comp_code = get_comp_code(request)
    agent_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'AGENT')
    return {
        'agent_data': agent_data
        }

def get_staff_category(request):
    comp_code = get_comp_code(request)
    staff_category_data = CodeMaster.objects.filter(comp_code=comp_code, is_active='Y', base_type = 'STAFF_CATEGORY')
    return {
        'staff_category_data': staff_category_data
        }
