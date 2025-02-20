from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import PaycycleMaster
from django.utils.timezone import now
from datetime import datetime
from django.http import JsonResponse
from .models import projectMatster
import  uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import CodeMaster



class Paycycle(View):
    template_name = "pages/payroll/paycycle_master/paycycle-list.html"

    def get(self, request):
        paycycle_list = PaycycleMaster.objects.filter(comp_code='1000', is_active="Y")
        return render(request, self.template_name, {"paycycle_list": paycycle_list})

    def post(self, request):
        process_cycle_id = request.POST.get('process_cycle_id')
        process_description = request.POST.get('process_description')
        process_cycle = request.POST.get('process_cycle')
        pay_process_month = request.POST.get('pay_process_month')
        date_from = self.parse_date(request.POST.get('date_from'))
        date_to = self.parse_date(request.POST.get('date_to'))
        process_date = self.parse_date(request.POST.get('process_date'))
        attendance_uom = request.POST.get('attendance_uom')
        default_project = request.POST.get('default_project')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        hours_per_day = request.POST.get('hours_per_day')
        days_per_month = request.POST.get('days_per_month')
        travel_time = request.POST.get('travel_time')
        lunch_break = request.POST.get('lunch_break')
        ot_eligible = request.POST.get('ot_eligible')
        ot2_eligible = request.POST.get('ot2_eligible')
        max_mn_hrs = request.POST.get('max_mn_hrs')
        max_an_hrs = request.POST.get('max_an_hrs')
        max_ot1_hrs = request.POST.get('max_ot1_hrs')
        ot1_amt = request.POST.get('ot1_amt')
        max_ot2_hrs = request.POST.get('max_ot2_hrs')
        ot2_amt = request.POST.get('ot2_amt')
        process_comp_flag = int(request.POST.get('process_comp_flag', 0))
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
            print(f" Error: {str(e)}")  
        
    
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
    return render(request, template_name, {'projects': projects})


def delete_project(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")

        if project_id:
            project = get_object_or_404(projectMatster, project_id=project_id)
            project.is_active = False  
            project.save()
    return redirect("project")



class CodeMasterList(View):

    template_name = "pages/payroll/code_master/code_master_list.html"

    def get(self, request):
        base_type_suggestions = CodeMaster.objects.filter(comp_code="999").values("base_description", "base_value").distinct()
        base_type_comp_code = CodeMaster.objects.filter(comp_code="1000", is_active = 'Y').values("base_type").distinct()
        return render(request, self.template_name, { "base_type_suggestions": base_type_suggestions, "base_type_comp_code": base_type_comp_code })

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return self.handle_ajax(request)
        return self.handle_form_submission(request)

    def handle_ajax(self, request):
        base_type = request.POST.get("base_type")
        base_value = request.POST.get("base_value")
        description = request.POST.get("description")
        delete_flag = request.POST.get("delete")

        # Handling delete request
        if delete_flag:
            try:
                code_master = CodeMaster.objects.get(base_type=base_type, base_value=base_value, comp_code="1000")
                code_master.is_active = "N"  
                code_master.save()
                return JsonResponse({"success": True})
            except CodeMaster.DoesNotExist:
                return JsonResponse({"success": False, "error": "Entry not found."})
        
        # Handling description update request
        if description:
            try:
                code_master = CodeMaster.objects.get(base_type=base_type, base_value=base_value, comp_code="1000")
                code_master.base_description = description
                code_master.save()
                return JsonResponse({"success": True})
            except CodeMaster.DoesNotExist:
                return JsonResponse({"success": False, "error": "Entry not found."})
        else:
            if base_value:
                base_values = CodeMaster.objects.filter(base_type=base_type, comp_code="1000").values_list("base_value", flat=True)
                exists = CodeMaster.objects.filter(base_value=base_value, base_type=base_type, comp_code="1000").exists()
                return JsonResponse({"exists": exists, "base_values": list(base_values)})
            else:
                base_values = CodeMaster.objects.filter(base_type=base_type, comp_code="1000", is_active = 'Y').values("base_value", "base_description")
                return JsonResponse({"base_values": list(base_values)})

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


from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import UserMaster
from django.http import JsonResponse
from django.core.exceptions import ValidationError

class Login(View):
    template_name = 'auth/login.html'
    
    def get(self, request):
        return render(request, self.template_name)

class UserMasterList(View):
    template_name = 'pages/payroll/user/user_master.html'

    def get(self, request):
        users = UserMaster.objects.all()
        return render(request, self.template_name, {'users': users})

class UserMasterCreate(View):
    def post(self, request):
        try:
            created_by = request.POST.get('created_by')
            modified_by = request.POST.get('modified_by')

            user = UserMaster(
                comp_code=request.POST.get('comp_code'),
                user_master_id=request.POST.get('user_master_id'),  
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                user_id=request.POST.get('user_id'),
                password=request.POST.get('password'),
                dob=request.POST.get('dob'),
                email=request.POST.get('email'),
                gender=request.POST.get('gender'),
                is_active=request.POST.get('is_active') == 'on',  # Checkbox handling
                instance_id=request.POST.get('instance_id'),
                profile_picture=request.FILES.get('profile_picture'), 
                created_by=created_by,
                modified_by=modified_by,
                emp_code=request.POST.get('emp_code'),
                user_paycycles=request.POST.get('user_paycycles')
            )

            # Validate and save the instance
            user.full_clean()  
            user.save()

            return redirect('user_list')
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})

class UserMasterUpdate(View):
    def post(self, request, user_master_id):
        try:
            user = get_object_or_404(UserMaster, user_master_id=user_master_id)
            user.comp_code = request.POST.get('comp_code')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.user_id = request.POST.get('user_id')
            user.password = request.POST.get('password')
            user.dob = request.POST.get('dob')
            user.email = request.POST.get('email')
            user.gender = request.POST.get('gender')
            user.instance_id = request.POST.get('instance_id')
            user.profile_picture = request.FILES.get('profile_picture')
            user.modified_by = request.POST.get('modified_by')
            user.emp_code = request.POST.get('emp_code')
            user.user_paycycles = request.POST.get('user_paycycles')
            user.is_active = request.POST.get('is_active') == 'on'  # Checkbox handling
            user.full_clean() 
            user.save()
            return redirect('user_list')
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

class UserMasterDelete(View):
    def post(self, request, user_master_id):
        
        user = get_object_or_404(UserMaster, user_master_id=user_master_id)
        
        user.is_active = False
        user.save()  
        
        return redirect('user_list')