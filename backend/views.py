from django.views.generic import *;
from django.http import HttpRequest, HttpResponse;
from django.shortcuts import render, redirect;
from django.contrib.auth import *;

from models import *

# create your own views here

class LoginView(FormView):
    template_name = 'login.html'
    
    def get(self, req:HttpRequest):
        if(req.user.is_authenticated != True):
            return render(req, self.template_name, {})
        else:
            return redirect('/patient/'+str(req.user.id))

class Login(LoginView):
    
    def post(self, req:HttpRequest):
        username = req.POST.get('sesion_username')
        password = req.POST.get('sesion_password')
        
        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            
            patient = Patient.objects.get(SystemUser.id == user.id)
            worker = Worker.objects.get(SystemUser.id == user.id)
            
            
            return redirect('/patient/'+str(user.id))
        
        return HttpResponse('No logged'+username+' -- '+password)
    
class AdminProfileView(DetailView):
    template_name = 'admin_profile.html'
    
    def get(self, req:HttpRequest, id:int):
        return render(req, self.template_name, {})


class PatientProfileView(DetailView):
    template_name = 'user_profile.html'
    
    def get(self, req:HttpRequest, id:int):
        return render(req, self.template_name, {})


class WorkerProfileView(DetailView):
    template_name = 'worker_profile.html'
    
    def get(self, req:HttpRequest, id:int):
        return render(req, self.template_name, {})

class WorkerListView(ListView):
    template_name = 'worker_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

class UserListView(ListView):
    template_name = 'user_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

class TaskList(ListView):
    template_name = 'task_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

class ResultList(ListView):
    template_name = 'result_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})




