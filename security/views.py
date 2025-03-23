from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import RoleMaster
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

PAGINATION_SIZE = 6

class RoleMasterList(View):
    template_name = 'pages/security/role/role_master.html'

    def get(self, request):
        keyword = request.GET.get('keyword', '').strip()
        page_number = request.GET.get('page', 1)
        get_url = request.get_full_path()

        # Adjust URL for pagination
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        # Initialize the query
        query = RoleMaster.objects.all()

        # Apply search filter if a keyword is provided
        if keyword:
            try:
                query = query.filter(
                    Q(role_name__icontains=keyword) |
                    Q(role_description__icontains=keyword)
                )
            except Exception as e:
                print(f"Error in keyword search: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

        # Apply pagination
        paginator = Paginator(query.order_by('-created_on'), PAGINATION_SIZE)

        try:
            roles_page = paginator.get_page(page_number)
        except PageNotAnInteger:
            roles_page = paginator.page(1)
        except EmptyPage:
            roles_page = paginator.page(paginator.num_pages)

        # Prepare the context for the template
        context = {
            'roles': roles_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': query.count()
        }

        return render(request, self.template_name, context)

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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

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
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page', 1)
    get_url = request.get_full_path()

    # Adjust URL for pagination
    if '?keyword' in get_url:
        get_url = get_url.split('&page=')[0]
        current_url = f"{get_url}&"
    else:
        get_url = get_url.split('?')[0]
        current_url = f"{get_url}?"

    # Initialize the query
    query = UserRoleMapping.objects.all()

    # Apply search filter if a keyword is provided
    if keyword:
        try:
            query = query.filter(
                Q(userid__icontains=keyword) |
                Q(roleid__icontains=keyword)
            )
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid search keyword'}, status=400)

    # Apply pagination
    paginator = Paginator(query.order_by('-created_on'), PAGINATION_SIZE)

    try:
        mappings_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        mappings_page = paginator.page(1)
    except EmptyPage:
        mappings_page = paginator.page(paginator.num_pages)

    # Prepare the context for the template
    users = UserMaster.objects.filter(is_active=True)
    roles = RoleMaster.objects.filter(is_active=True)
    context = {
        'mappings': mappings_page,
        'users': users,
        'roles': roles,
        'current_url': current_url,
        'keyword': keyword,
        'result_cnt': query.count()
    }

    return render(request, 'pages/security/user_role_mapping/user_role_mapping.html', context)