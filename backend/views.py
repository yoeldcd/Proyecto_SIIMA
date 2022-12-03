from django.views.generic import *;
from django.http import HttpRequest, HttpResponse;
from django.shortcuts import render, redirect;
from django.contrib.auth import *;

from .models import *

# create your own views here

###############################################################################

class LoginView(FormView):
    template_name = 'login.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})
        
###############################################################################

class AuthView(LoginView):
    
    def post(self, req:HttpRequest):
        username = req.POST.get('sesion_username')
        password = req.POST.get('sesion_password')
        
        # close autenticated user sesion
        if(req.user.is_authenticated == True):
            logout(req)
            return redirect('/login')
        
        user = authenticate(req, username=username, password=password)
        
        # notify auth Error
        if user is None:
            return HttpResponse(f'No registred User [ username: {username}, password {password} ]')
        
        # start new user sesion
        login(req, user)
        
        # select profile page type
        if PatientManager.is_patient_user(user=user):
            return redirect('/patient/'+str(user.id))
        else:
            return redirect('/worker/'+str(user.id))
        
###############################################################################

class PatientProfileView(DetailView):
    template_name = 'user_profile.html'
    
    def get(self, req:HttpRequest, id:int):
        patient = PatientManager.get_patient_user(req.user)
        
        return render(req, self.template_name, {'patient': patient})

        
###############################################################################

class WorkerProfileView(DetailView):
    template_name = 'worker_profile.html'
    
    def get(self, req:HttpRequest, id:int):
        worker = WorkerManager.get_worker_user(req.user)
        
        return render(req, self.template_name, {'worker': worker})

###############################################################################

class WorkerListView(ListView):
    template_name = 'worker_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

###############################################################################

class UserListView(ListView):
    template_name = 'user_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

###############################################################################

class TaskList(ListView):
    template_name = 'task_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

###############################################################################

class ResultList(ListView):
    template_name = 'result_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

