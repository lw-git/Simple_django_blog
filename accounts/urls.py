from django.urls import path
from .views import SignupView
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
]
