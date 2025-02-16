from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import PaycycleMaster
from django.utils.timezone import now
from datetime import datetime
from django.http import JsonResponse

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
