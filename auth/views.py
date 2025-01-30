
from django.shortcuts import render
from django.views import View

class Login(View):
    template_name = 'auth/login.html'
    def get(self, request):
        return render(request, self.template_name)
