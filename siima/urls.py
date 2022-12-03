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
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User role pages
    path('patient/sigin/', SiginView.as_view(), name='sigin_patient'),
    path('patient/<int:user_id>', login_required(PatientProfileView.as_view()), name='patient'),
    path('results/', login_required(PatientProfileView.as_view()), name='results'),
    
    # Worker role pages
    path('worker/<int:user_id>/', login_required(WorkerProfileView.as_view()), name='worker'),
    path('tests/', login_required(WorkerProfileView.as_view()), name='tests'),
    path('patients/', login_required(WorkerProfileView.as_view()), name='patients'),
    path('workers/', login_required(WorkerProfileView.as_view()), name='workers'),
    path('events/', login_required(WorkerProfileView.as_view()), name='events'),
    

]
