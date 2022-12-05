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
    path('logout/', LoginView.as_view(), name='logout'),
    path('auth/', AuthView.as_view(), name='auth'),
    
    # User role views
    path('patients/', login_required(PatientListView.as_view()), name='patients'),
    path('patient/sigin/', login_required(SiginPatientView.as_view()), name='sigin_patient'),
    path('patient/edit/<int:user_id>', login_required(EditPatientView.as_view()), name='sigin_patient'),
    path('patient/update/<int:user_id>', login_required(EditPatientView.as_view()), name='sigin_patient'),
    path('patient/<int:user_id>', login_required(PatientProfileView.as_view()), name='patient'),
    
    # Worker role views
    path('workers/', login_required(WorkerListView.as_view()), name='workers'),
    path('worker/sigin/', login_required(SiginWorkerView.as_view()), name='sigin_worker'),
    path('worker/edit/<int:user_id>', login_required(EditWorkerView.as_view()), name='sigin_patient'),
    path('worker/update/<int:user_id>', login_required(EditWorkerView.as_view()), name='sigin_patient'),
    path('worker/<int:user_id>/', login_required(WorkerProfileView.as_view()), name='worker'),
    
    # test edition views
    path('tests/', login_required(TestListView.as_view()), name='tests'),
    path('tests/add/', login_required(TestAddView.as_view()), name='add_test'),
    path('tests/resolve/', login_required(TestResolveView.as_view()), name='resolve_test'),
    
    # Model lists
    path('results/', login_required(ResultListView.as_view()), name='results'),
    path('events/', login_required(EventListView.as_view()), name='events'),
    
]
