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
            if RoleMaster.objects.filter(role_name=role_name).exists():
                return JsonResponse({'status': 'error', 'message': 'Role name already exists.', 'field': 'role_name'})
            created_by = request.POST.get('created_by')
            modified_by = request.POST.get('modified_by')
            role = RoleMaster(
                comp_code=request.POST.get('comp_code'),
                role_name=role_name,
                role_description=request.POST.get('role_description'),
                is_active=request.POST.get('is_active') == 'on',
                created_by=1,
                modified_by=1,
            )
            role.full_clean()  
            role.save()
            return redirect('role_list')
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

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from .models import UserRoleMapping
from payroll.models import UserMaster
from security.models import RoleMaster

class UserRoleMappingCreate(View):
    def get(self, request):
        users = UserMaster.objects.filter(is_active=True)
        roles = RoleMaster.objects.filter(is_active=True)
        return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
            'users': users,
            'roles': roles,
            'mappings': UserRoleMapping.objects.all()
        })

    def post(self, request):
        try:
            user_master_id = request.POST.get('user_master_id')
            user_master = get_object_or_404(UserMaster, user_master_id=user_master_id)
            roleid = request.POST.get('roleid')
            role = get_object_or_404(RoleMaster, id=roleid)

            # Check if the user already has a role assigned
            if UserRoleMapping.objects.filter(userid=user_master.user_master_id).exists():
                return JsonResponse({'error': 'User has already been assigned a role.'}, status=400)

            mapping = UserRoleMapping(
                comp_code=1000,
                userid=user_master.user_master_id,
                roleid=role.id,
                role_start_date=request.POST.get('role_start_date'),
                role_to_date=request.POST.get('role_to_date'),
                is_active=request.POST.get('is_active') == 'on',
                created_by=4  # Hard-coded value
            )
            mapping.full_clean()
            mapping.save()
            return JsonResponse({'success': 'User role mapping created successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class UserRoleMappingUpdate(View):
    def post(self, request, mappingid):
        try:
            mapping = get_object_or_404(UserRoleMapping, mappingid=mappingid)
            user_master_id = request.POST.get('user_master_id')
            user_master = get_object_or_404(UserMaster, user_master_id=user_master_id)
            roleid = request.POST.get('roleid')
            role = get_object_or_404(RoleMaster, id=roleid)

            # Check if the user already has a role assigned (excluding the current mapping)
            if UserRoleMapping.objects.filter(userid=user_master.user_master_id).exclude(mappingid=mappingid).exists():
                return JsonResponse({'error': 'User has already been assigned a role.'}, status=400)

            mapping.userid = user_master.user_master_id
            mapping.roleid = role.id
            mapping.role_start_date = request.POST.get('role_start_date')
            mapping.role_to_date = request.POST.get('role_to_date')
            mapping.is_active = request.POST.get('is_active') == 'on'
            mapping.modified_by = 5  # Hard-coded value
            mapping.full_clean()
            mapping.save()
            return JsonResponse({'success': 'User role mapping updated successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class UserRoleMappingDelete(View):
    def post(self, request, mappingid):
        try:
            mapping = get_object_or_404(UserRoleMapping, mappingid=mappingid)
            mapping.is_active = False
            mapping.save()
            return redirect('user_role_mapping_list')
        except Exception as e:
            users = UserMaster.objects.filter(is_active=True)
            return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
                'error': str(e),
                'mappings': UserRoleMapping.objects.all(),
                'users': users
            })
        


def user_role_mapping_list(request):
    mappings = UserRoleMapping.objects.all()
    users = UserMaster.objects.filter(is_active=True)
    roles = RoleMaster.objects.filter(is_active=True)
    return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
        'mappings': mappings,
        'users': users,
        'roles': roles
    })