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
    
    # uthentication views
    path('', LoginView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LoginView.as_view(), name='logout'),
    path('auth/', AuthView.as_view(), name='auth'),
    
    # patients's management views
    path('patients/', login_required(PatientListView.as_view()), name='patients'),
    path('patient/sigin/', SiginPatientView.as_view(), name='sigin_patient'),
    path('patient/edit/<int:user_id>', login_required(EditPatientView.as_view()), name='sigin_patient'),
    path('patient/update/<int:user_id>', login_required(EditPatientView.as_view()), name='sigin_patient'),
    path('patient/supress/<int:user_id>', login_required(SignoutPatientView.as_view()), name='sigou_patient'),
    path('patient/<int:user_id>', login_required(PatientProfileView.as_view()), name='patient'),
    
    # worker's management views
    path('workers/', login_required(WorkerListView.as_view()), name='workers'),
    path('worker/sigin/', SiginWorkerView.as_view(), name='sigin_worker'),
    path('worker/edit/<int:user_id>', login_required(EditWorkerView.as_view()), name='sigin_patient'),
    path('worker/update/<int:user_id>', login_required(EditWorkerView.as_view()), name='sigin_patient'),
    path('worker/supress/<int:user_id>', login_required(SignoutWorkerView.as_view()), name='sigin_patient'),
    path('worker/<int:user_id>/', login_required(WorkerProfileView.as_view()), name='worker'),
    path('admin/<int:user_id>/', login_required(WorkerProfileView.as_view()), name='admin'),
    
    # test management views
    path('tests/', login_required(TestListView.as_view()), name='tests'),
    path('test/add/', login_required(AddTestView.as_view()), name='add_test'),
    path('test/resolve/<int:test_id>', login_required(ResolveTestView.as_view()), name='resolve_test'),
    path('test/notify/<int:test_id>', login_required(NotifyTestView.as_view()), name='notify_test'),
    
    # result management views
    path('results/', login_required(ResultListView.as_view()), name='results'),
    path('result/supress/<int:test_id>', login_required(SupressResultView.as_view()), name='supress_result'),
    
    # events management views
    path('events/', login_required(EventListView.as_view()), name='events'),
    path('event/supress/<int:event_id>', login_required(SupressEventView.as_view()), name='supress_event'),
    
]

make_custom_permissions()
