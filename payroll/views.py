from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse
from .models import projectMatster
from django.utils.timezone import now
import  uuid
from django.views.decorators.csrf import csrf_exempt


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
