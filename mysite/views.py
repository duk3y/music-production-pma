from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views import View

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CommonDefaultView(View):
    template_name = 'commondefault.html'

    def get(self, request):
        return render(request, self.template_name)

class PMAAdminDefaultView(View):
    template_name = 'pmaadmindefault.html'

    def get(self, request):
        return render(request, self.template_name)    