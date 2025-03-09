from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import RoleMaster
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.urls import reverse

class RoleMasterList(View):

    template_name = 'pages/security/role/role_master.html'

    def get(self, request):
        roles = RoleMaster.objects.all()
        return render(request, self.template_name, {'roles': roles})

class RoleMasterCreate(View):

    def post(self, request):
        try:
            role_name = request.POST.get('role_name')
            
            # Check for duplicate role name
            if RoleMaster.objects.filter(role_name=role_name).exists():
                return JsonResponse({'status': 'error', 'message': 'Role name already exists.', 'field': 'role_name'})
            
            created_by = request.POST.get('created_by')
            modified_by = request.POST.get('modified_by')
            role = RoleMaster(
                comp_code=request.POST.get('comp_code'),
                role_name=role_name,
                role_description=request.POST.get('role_description'),
                is_active=request.POST.get('is_active') == 'on',
                created_by=created_by,
                modified_by=modified_by,
            )
            role.full_clean()  
            role.save()

            return JsonResponse({'status': 'success', 'redirect_url': reverse('role_list')})
        
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

class RoleMasterUpdate(View):

    def post(self, request, role_id):

        try:
            role = get_object_or_404(RoleMaster, id=role_id)
            role.comp_code = request.POST.get('comp_code')
            role.role_description = request.POST.get('role_description')
            role.modified_by = request.POST.get('modified_by')
            
            role.is_active = request.POST.get('is_active') == 'on'
            role.full_clean() 
            role.save()
            return redirect('role_list')
        
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

class RoleMasterDelete(View):

    def post(self, request, role_id):
        try:
            role = get_object_or_404(RoleMaster, id=role_id)
            
            role.is_active = False
            role.save()
            
            return redirect('role_list')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})