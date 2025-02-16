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