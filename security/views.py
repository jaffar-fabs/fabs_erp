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
        

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import UserRoleMapping 
from payroll.models import UserMaster
from django.urls import reverse

class UserRoleMappingCreate(View):
    def get(self, request):
        # Fetch active users for the dropdown
        users = UserMaster.objects.filter(is_active=True)
        return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
            'users': users,
            'mappings': UserRoleMapping.objects.all()
        })

    def post(self, request):
        try:
            # Hardcode comp_code and set created_by to the current user's ID
            mapping = UserRoleMapping(
                comp_code=1000,  # Hardcoded value
                userid=request.POST.get('userid'),
                roleid=request.POST.get('roleid'),
                role_start_date=request.POST.get('role_start_date'),
                role_to_date=request.POST.get('role_to_date'),
                is_active=request.POST.get('is_active') == 'on',
                created_by=request.POST.get('created_by')  # Manually entered
            )
            mapping.full_clean()  # Validate the model
            mapping.save()
            return redirect('user_role_mapping_list')  # Redirect to the list view
        except Exception as e:
            # Pass the error message to the template with field-specific errors
            users = UserMaster.objects.filter(is_active=True)  # Fetch users again in case of error
            return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
                'error': str(e),
                'field_errors': {'userid': str(e)},  # Pass field-specific errors
                'mappings': UserRoleMapping.objects.all(),
                'users': users  # Pass users to the template
            })

class UserRoleMappingUpdate(View):
    def post(self, request, mappingid):
        try:
            mapping = get_object_or_404(UserRoleMapping, mappingid=mappingid)
            mapping.userid = request.POST.get('userid')
            mapping.roleid = request.POST.get('roleid')
            mapping.role_start_date = request.POST.get('role_start_date')
            mapping.role_to_date = request.POST.get('role_to_date')
            mapping.is_active = request.POST.get('is_active') == 'on'  # Update is_active status
            mapping.modified_by = request.POST.get('modified_by')  # Manually entered
            mapping.full_clean()  # Validate the model
            mapping.save()
            return redirect('user_role_mapping_list')  # Redirect to the list view
        except Exception as e:
            # Pass the error message to the template with field-specific errors
            users = UserMaster.objects.filter(is_active=True)  # Fetch users again in case of error
            return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
                'error': str(e),
                'field_errors': {'userid': str(e)},  # Pass field-specific errors
                'mappings': UserRoleMapping.objects.all(),
                'users': users  # Pass users to the template
            })

class UserRoleMappingDelete(View):
    def post(self, request, mappingid):
        try:
            mapping = get_object_or_404(UserRoleMapping, mappingid=mappingid)
            mapping.is_active = False  # Mark as inactive instead of deleting
            mapping.save()
            return redirect('user_role_mapping_list')  # Redirect to the list view
        except Exception as e:
            # Pass the error message to the template
            users = UserMaster.objects.filter(is_active=True)  # Fetch users again in case of error
            return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
                'error': str(e),
                'mappings': UserRoleMapping.objects.all(),
                'users': users  # Pass users to the template
            })

def user_role_mapping_list(request):
    mappings = UserRoleMapping.objects.all()  # Fetch all mappings, both active and inactive
    users = UserMaster.objects.filter(is_active=True)  # Fetch all active users
    return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', {
        'mappings': mappings,
        'users': users  # Pass users to the template
    })