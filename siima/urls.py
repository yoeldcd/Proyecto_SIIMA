"""siima URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from cmath import log
from django.contrib import admin
from django.urls import path

from siima.endpoint import tools
from siima.endpoint.views import login, user_profile, worker_profile, admin_profile


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Coomn role pages
    path('login/', login.get),
    
    # User role pages
    path('profile/', user_profile.get),
    #path('edit-user-profile/', index.edit_user_profile),
    #path('test-log/', index.test_log),
    
    # Admin role pages
    path('admin_profile/', admin_profile.get),
    #path('users-list/', index.users_list),
    #path('workers-list/', index.workers_list),
    #path('events-log/', index.events_log),
    
    # Worker role pages
    path('worker_profile/', worker_profile.get),
    #path('edit-worker-profile/', index.edit_worker_profile),
    #path('test-edition/', index.test_edition),
    
]
