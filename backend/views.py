from django.views.generic import *;
from django.http import HttpRequest, HttpResponse;
from django.shortcuts import render;

# create your own views here

class LoginView(View):
    template_name = 'login.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})


class AdminProfileView(DetailView):
    template_name = 'admin_profile.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})


class PatientProfileView(DetailView):
    template_name = 'user_profile.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})


class WorkerProfileView(DetailView):
    template_name = 'worker_profile.html'
    
    def get(self, req:HttpRequest):
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




