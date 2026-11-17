from django.contrib.auth.views import LoginView

from .forms import FormularioLogin


class LoginComBloqueioView(LoginView):
    template_name = "registration/login.html"
    authentication_form = FormularioLogin
    redirect_authenticated_user = True
