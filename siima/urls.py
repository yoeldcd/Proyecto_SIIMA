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
    
    # Authentication page
    path('', LoginView.as_view()),
    path('login/', LoginView.as_view()),
    path('start_sesion/', Login.as_view()),
    
    # User role pages
    path('patient/<int:id>', login_required(PatientProfileView.as_view())),
    
    # Admin role pages
    path('admin/<int:id>', login_required(AdminProfileView.as_view())),
    
    # Worker role pages
    path('worker/<int:id>', login_required(WorkerProfileView.as_view())),
    
]
