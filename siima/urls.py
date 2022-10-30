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

from siima.endpoint.views import login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login.get),
    
    # User pages
    path('user-profile/', index.user_profile),
    path('edit-user-profile/', index.edit_user_profile),
    path('test-log/', index.test_log),
    
    # Admin pages
    path('admin-profile/', index.admin_profile),
    path('users-list/', index.users_list),
    path('workers-list/', index.workers_list),
    path('events-log/', index.events_log),
    
    # Worker pages
    path('worker-profile/', index.worker_profile),
    path('edit-worker-profile/', index.edit_worker_profile),
    path('test-edition/', index.test_edition),
    
    # Others
    path('', index.load_url)
]
