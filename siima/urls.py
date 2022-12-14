"""siima URL Configuration"""

from django.urls import path

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from backend.views import *

urlpatterns = [
    
    # uthentication views
    path('', LoginView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LoginView.as_view(), name='logout'),
    path('auth/', AuthView.as_view(), name='auth'),
    
    # patients's management views
    path('patients/', login_required(PatientListView.as_view()), name='patients'),
    path('patient/sigin/', SiginPatientView.as_view(), name='sigin_patient'),
    path('patient/edit/<int:user_id>', login_required(EditPatientView.as_view()), name='edit_patient'),
    path('patient/update/<int:user_id>', login_required(UpdatePatientView.as_view()), name='update_patient'),
    path('patient/supress/<int:user_id>', login_required(SignoutPatientView.as_view()), name='signout_patient'),
    path('patient/', login_required(PatientProfileView.as_view()), name='patient'),
    
    # worker's management views
    path('workers/', login_required(WorkerListView.as_view()), name='workers'),
    path('worker/sigin/', SiginWorkerView.as_view(), name='sigin_worker'),
    path('worker/edit/<int:user_id>', login_required(EditWorkerView.as_view()), name='edit_worker'),
    path('worker/update/<int:user_id>', login_required(UpdateWorkerView.as_view()), name='update_worker'),
    path('worker/supress/<int:user_id>', login_required(SignoutWorkerView.as_view()), name='signout_worker'),
    path('worker/', login_required(WorkerProfileView.as_view()), name='worker'),
    path('admin/', login_required(WorkerProfileView.as_view()), name='admin'),
    
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
    path('events/supress/', login_required(SupressSelectedEventsView.as_view()), name='supress_event'),
    path('event/supress/<int:event_id>', login_required(SupressEventView.as_view()), name='supress_event'),
    
]

make_custom_permissions()
