# your_app/context_processors.py

from .models import CodeMaster,GradeMaster, Employee, projectMatster

def gender_data(request):
    gender_data = CodeMaster.objects.filter(comp_code=1000, base_type='SEX')
    return {
        'gender_data': gender_data
    }


def get_paycycle(request):
    paycycle_data = CodeMaster.objects.filter(comp_code=1000, base_type='PROCESS CYCLE')
    return {   
        'paycycle_data': paycycle_data
        }

def get_status(request):
    status_data = CodeMaster.objects.filter(comp_code=1000, base_type='STATUS')
    return {
        'status_data': status_data
        }

def mar_status(request):
    mar_status_data = CodeMaster.objects.filter(comp_code=1000, base_type='MARITAL STATUS')
    return {
         'mar_status_data': mar_status_data
         }

def desig(request):
    desig_data = CodeMaster.objects.filter(comp_code=1000, base_type='DESIGNATION')
    return {
         'desig_data': desig_data
         }

def dept(request):
    dept_data = CodeMaster.objects.filter(comp_code=1000, base_type='DEPT')
    return {
         'dept_data': dept_data
         }

def process_flag(request):
    pf_data = CodeMaster.objects.filter(comp_code=1000, base_type='PROCESS COMPLETION FLAG')
    return {
         'pf_data': pf_data
         }

def at_uom(request):
    at_uom_data = CodeMaster.objects.filter(comp_code=1000, base_type='ATTENDANCE UOM')
    return {
         'at_uom_data': at_uom_data
         }

def pro_type(request):
    pro_type_data = CodeMaster.objects.filter(comp_code=1000, base_type='PROJECT TYPE')
    return {
         'pro_type_data': pro_type_data
         }


def pro_city(request):
    pro_city_data = CodeMaster.objects.filter(comp_code=1000, base_type='PROJECT CITY')
    return {
         'pro_city_data': pro_city_data
         }

def nationality(request):
    nation_data = CodeMaster.objects.filter(comp_code=1000, base_type='NATIONALITY')
    return {
         'nation_data': nation_data
         }

def hol_type(request):
    hol_type_data = CodeMaster.objects.filter(comp_code=1000, base_type='HOLIDAY')
    return {
         'hol_type_data': hol_type_data
         }

def grade_code(request):
    grade_code_data = GradeMaster.objects.filter(comp_code=1000, is_active = 'Y')
    return {
        'grade_code_data': grade_code_data
        }

def project(request):
    project_data = projectMatster.objects.filter(comp_code=1000, is_active= True)
    return {
        'project_data': project_data
        }

def employee(request):
    employee_data = Employee.objects.filter(comp_code=1000)
    return {
        'employee_data': employee_data
        }