"""siima URL Configuration"""

from datetime import *
from cmath import log
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import path

from backend.views import *

urlpatterns = [
    #path('admin/', admin.sites.site.urls),
    
    # Authentication pages
    path('', LoginView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('auth/', AuthView.as_view(), name='auth'),
    path('logout/', AuthView.as_view(), name='logout'),
    
    # User role pages
    path('patient/<int:id>', login_required(PatientProfileView.as_view())),
    
    # Worker role pages
    path('worker/<int:id>', login_required(WorkerProfileView.as_view())),
    
]
