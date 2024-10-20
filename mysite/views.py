from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from users.models import Profile



def home(request):
    return render(request, 'home.html')

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


@login_required()
def AuthenticationView(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    # print(Profile.pmaStatus)
    if profile.pmaStatus:
        print("yes")
        return redirect(reverse("pma_admin_default"))
    else:
        print("no")
        return redirect(reverse("common_default"))
