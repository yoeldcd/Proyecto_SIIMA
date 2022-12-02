"""siima URL Configuration"""

from datetime import *
from cmath import log
from django.contrib import admin
from django.urls import path

from backend.views import *
from backend.models import *

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Coomn role pages
    path('', LoginView.as_view()),
    path('login/', LoginView.as_view()),
    
    # User role pages
    path('profile/user/<int:id>', PatientProfileView.as_view()),
    
    # Admin role pages
    path('profile/admin/<int:id>', AdminProfileView.as_view()),
    
    # Worker role pages
    path('profile/worker/<int:id>', WorkerProfileView.as_view()),

    
]

test = Test(None, patientCI = '99040710729', testID = '4', result = 'resultato', begin_date = date(2022,12,1), resolution_date = date(2022,12,2))
test.save()