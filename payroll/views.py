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