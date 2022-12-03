from datetime import *

from django.views.generic import *;
from django.http import HttpRequest, HttpResponse;
from django.shortcuts import render, redirect;
from django.contrib.auth import *;
from django.urls import *

from .models import *

# create your own views here

###############################################################################

class LoginView(FormView):
    template_name = 'login.html'
    
    def get(self, req:HttpRequest):
        
        context = {
            'current_time': datetime.utcnow,
        }
        
        return render(req, self.template_name, {})

###############################################################################

PROFILES = {
    'ADMIN':'ADMIN',
    'WORKER':'WORKER',
    'PATIENT':'PATIENT'
}

class AuthView(LoginView):
    
    def post(self, req:HttpRequest):
        username = req.POST.get('username')
        password = req.POST.get('password')
        
        # close autenticated user sesion
        user = authenticate(username=username, password=password)
        
        # notify auth Error
        if user is None:
            return HttpResponse(f'No registred User [ username: {username}, password {password} ]')
            
        # start new user sesion
        login(req, user)
        print('loged'+str(req.user.id))
        
        # select profile page type
        if PatientManager.is_patient_user(user=user):
            return redirect('/patient/'+str(user.id))
        else:
            return redirect('/worker/'+str(user.id))

class LogoutView(View):

    def get(self, req:HttpRequest):
        
        # finsh current user sesion
        if(req.user.is_authenticated == True):
            logout(req)
            print('logout '+str(req.user.id))
        
        return redirect('/login')
        

###############################################################################

class PatientProfileView(DetailView):
    template_name = 'patient_profile.html'
    
    def get(self, req:HttpRequest, user_id:int):
        patient = PatientManager.get_patient_user(req.user)
        
        # define context values
        context = {
            'current_time': datetime.utcnow,
            'profile_type': PROFILES['PATIENT'],
            'profile_url': reverse('patient', kwargs = {'user_id': user_id}),
            'profile_icon': patient.icon_path,
            'patient': patient
        }
        
        return render(req, self.template_name, context)

class SiginView(View):
    
    def post(self, req:HttpRequest):
        params = req.POST
        
        # registre new params user
        Patient.objects.create_user(
            username = params.get('username'),
            password = params.get('password'),
            email = params.get('email'),
            ci = params.get('ci'),
            first_name = params.get('first_name'),
            last_name = params.get('last_name'),
            blod_group = params.get('blod_group_letter') + params.get('blod_group_signus'),
            sex = params.get('sex'),
            age = params.get('age'),
            phone = params.get('phone'),
        ).save()
        
        return redirect('auth')
        
###############################################################################

class WorkerProfileView(DetailView):
    template_name = 'worker_profile.html'
    
    def get(self, req:HttpRequest, user_id:int):
        worker = WorkerManager.get_worker_user(req.user)
        
        # define context values from template rendering
        context = {
            'current_time': datetime.utcnow,
            'profile_type': PROFILES['WORKER'],
            'profile_url': reverse('worker', kwargs = {'user_id': user_id}),
            #'profile_icon': worker.icon_path,
            'profile_icon': '/static/img/profiles/default_profile.png',
            'worker': worker
        }
        
        # declare admin profile type
        if req.user.is_staff:
            context['profile_type'] = PROFILES['ADMIN']
        
        return render(req, self.template_name, context)

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

