from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.shortcuts import redirect


class SignupView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def dispatch(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:
            return redirect(reverse('home'))

        return super().dispatch(request, *args, **kwargs)
