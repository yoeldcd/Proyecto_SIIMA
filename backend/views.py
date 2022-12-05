
from datetime import datetime

from django.utils.http import urlencode
from django.http import HttpRequest, HttpResponse;
from django.shortcuts import render, redirect;
from django.views.generic import *;
from django.urls import *
from django.contrib.auth import *;
from django.contrib.auth.mixins import *;
from django.contrib.auth.decorators import *

from .models import *

# create your own views here

PROFILES_ICON_DIR = '/static/img/profiles/'
PROFILES = {
    'ADMIN':'ADMIN',
    'WORKER':'WORKER',
    'PATIENT':'PATIENT'
}

# VISUAL ##############################################################################

class LoginView(FormView):
    template_name = 'login.html'
    
    def get(self, req:HttpRequest):
        query_message = req.GET.get('query_message')
        
        # logout current user
        if req.user.is_authenticated:
            query_message = f'{ req.user.username } HA SALIDO DEL SISTEMA'
            logout(req)
            
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'varA': 2
        }
        
        return render(req, self.template_name, context)

###############################################################################

class AuthView(LoginView):
    
    def get(self, req:HttpRequest):
        query_message = ""
        username = req.GET.get('username')
        password = req.GET.get('password')
        
        # close autenticated user sesion
        user = authenticate(username=username, password=password)
        
        # return back to login and notify auth Error
        if user is None:
            query_message = f'USUARIO {username} NO AUTENTICADO PW: {password}'
            return redirect(reverse('login')+'?'+urlencode({ 'query_message':query_message }))
        
        # start new user sesion
        login(req, user)
        
        # select profile page type
        if PatientManager.is_patient_user(user=user):
            return redirect('/patient/'+str(user.id))
        else:
            return redirect('/worker/'+str(user.id))

# VISUAL ##############################################################################

class PatientProfileView(PermissionRequiredMixin, DetailView):
    template_name = 'patient_profile.html'
    permission_required = ('backend.view_patient')

    def get(self, req:HttpRequest, user_id:int):
        
        systemuser = SystemUserManager.get_system_user(req.user)
        detailed_patient = PatientManager.get_patient_user(req.user)
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'profile_type': PROFILES['PATIENT'],
            'profile_url': reverse('patient', kwargs = {'user_id': user_id}),
            'profile_icon': PROFILES_ICON_DIR + systemuser.icon_path,
            'systemuser': systemuser,
            'detailed_patient': detailed_patient
        }
        
        return render(req, self.template_name, context)

###########################################

class SiginPatientView(View):
    
    def post(self, req:HttpRequest):
        query_message = ""
        params = req.POST
        
        # registre new patient user
        new_patient = PatientManager.create_patient_user(params)
        query_message = "SUCESS: Patient Profile Registred: " + params.get('username') + " PASSWORD " + params.get('password')
        
        # redirect admin to profile_page
        return redirect(reverse('auth')+'?'+urlencode({
            'username': params.get('username'),
            'password': params.get('password'),
            'query_message': query_message 
        }))

# VISUAL ##########################################

class EditPatientView(PermissionRequiredMixin, FormView):
    template_name = 'edit_patient.html'
    permission_required = ('backend.change_patient')
    
    def get(self, req:HttpRequest, user_id):
        q_params = req.GET
        query_message = q_params.get('query_message')
        
        systemuser = SystemUserManager.get_system_user(req.user)
        edited_patient = PatientManager.get_patient_user_by_id(user_id)
        
        # define context values
        context = {
            'profile_type': PROFILES['WORKER'],
            'current_time': datetime.now,
            'query_message': query_message,
            'profile_url': reverse('worker', kwargs = {'user_id': systemuser.id }),
            'profile_icon': PROFILES_ICON_DIR + systemuser.icon_path,
            'systemuser': systemuser,
            'edited_patient': edited_patient
        }
        
        if systemuser.is_superuser:
            context['profile_type'] = PROFILES['ADMIN']
        
        return render(req, self.template_name, context)
    
    def post(self, 
    req: HttpRequest, user_id : int):
        q_params = req.POST
        query_message = ""
        
        # check patient joined
        edited_patient = PatientManager.get_patient_user_by_id(user_id)
        
        if edited_patient is None:
            query_message = "ERROR No identified patient"
            return redirect(reverse('workers')+urlencode({'query_message': query_message}))
        
        # update patient profile
        PatientManager.update_patient_user(edited_patient, q_params)
        query_message = "SUCCESS: Pateint profile updated"
        
        # go back to patient list
        return redirect(reverse('patients')+'?'+urlencode({'query_message': query_message}))

# VISUAL ##########################################

class PatientListView(PermissionRequiredMixin, ListView):
    template_name = 'patient_list.html'
    permission_required = ('backend.edit_patient')
    
    def get(self, req:HttpRequest):
        
        systemuser = SystemUserManager.get_system_user(req.user)
        
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'profile_type': PROFILES['ADMIN'],
            'profile_url': reverse('worker', kwargs = {'user_id': req.user.id}),
            'profile_icon': PROFILES_ICON_DIR + systemuser.icon_path,
            'systemuser': systemuser,
            'object_list': PatientManager.list_all() 
        }
        
        return render(req, self.template_name, context)

# VISUAL ##############################################################################

class WorkerProfileView(PermissionRequiredMixin, DetailView):
    template_name = 'worker_profile.html'
    permission_required = ('backend.view_worker')
    
    def get(self, req:HttpRequest, user_id:int):
        
        systemuser = SystemUserManager.get_system_user(req.user)
        worker = WorkerManager.get_worker_user(req.user)
        
        # define context values from template rendering
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'profile_type': PROFILES['WORKER'],
            'profile_url': reverse('worker', kwargs = {'user_id': worker.id}),
            'profile_icon': PROFILES_ICON_DIR + systemuser.icon_path,
            'systemuser': systemuser,
            'detailed_worker': worker
        }
        
        # declare admin profile type
        if req.user.is_superuser:
            context['profile_type'] = PROFILES['ADMIN']
        
        return render(req, self.template_name, context)

###########################################

class SiginWorkerView(PermissionRequiredMixin, View):
    permission_required = ('backend.add_worker')
    
    def post(self, req:HttpRequest):
        params = req.POST
        
        # registre new worker user
        worker = WorkerManager.add_worker_user(params)
        query_message = "SUCCESS: Worker Profile Registred: " + params.get('username') + " PASSWORD " + params.get('password')
        
        # redirect admin to worker list
        return redirect(reverse('workers')+'?'+urlencode({
            'query_message': query_message 
        }))

# VISUAL ##########################################

class EditWorkerView(PermissionRequiredMixin, FormView):
    template_name = 'edit_worker.html'
    permission_required = ('backend.edit_worker')
    
    def get(self, req:HttpRequest, user_id):
        q_params = req.GET
        query_message = q_params.get('query_message')
        
        systemuser = SystemUserManager.get_system_user(req.user)
        edited_worker = WorkerManager.get_worker_user_by_id(user_id)
        
        # define context values
        context = {
            'profile_type': PROFILES['WORKER'],
            'current_time': datetime.now,
            'query_message': query_message,
            'profile_url': reverse('worker', kwargs = {'user_id': systemuser.id }),
            'profile_icon': PROFILES_ICON_DIR+'default_profile.png',
            'systemuser': systemuser,
            'edited_worker': edited_worker
        }
        
        if systemuser.is_superuser:
            context['profile_type'] = PROFILES['ADMIN']
        
        return render(req, self.template_name, context)
    
    def post(self, req: HttpRequest, user_id : int):
        q_params = req.POST
        query_message = ""
        
        # check worker joined
        edited_worker = WorkerManager.get_worker_user_by_id(user_id)
        
        if edited_worker is None:
            query_message = "ERROR No identified worker"
            return redirect(reverse('workers')+urlencode({'query_message': query_message}))
        
        # update worker profile
        WorkerManager.update_worker_user(edited_worker, q_params)
        query_message = "Worker profile updated"
        
        # go back to worker list
        return redirect(reverse('workers')+urlencode({'query_message': query_message}))
    
# VISUAL ##########################################

class WorkerListView(PermissionRequiredMixin, ListView):
    template_name = 'worker_list.html'
    permission_required = ('backend.edit_worker')
     
    def get(self, req:HttpRequest):
        
        systemuser = SystemUserManager.get_system_user(req.user)
        
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'profile_type': PROFILES['ADMIN'],
            'profile_url': reverse('worker', kwargs = {'user_id': systemuser.id}),
            'profile_icon': PROFILES_ICON_DIR + systemuser.icon_path,
            'systemuser': systemuser,
            'object_list': WorkerManager.list_all() 
        }
        
        return render(req, self.template_name, context)

# VISUAL ##############################################################################

class TestListView(PermissionRequiredMixin, ListView):
    template_name = 'test_list.html'
    permission_required = ('backend.edit_test')
    
    def get(self, req:HttpRequest):
        systemuser = SystemUserManager.get_system_user(req.user)
        
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'profile_type': PROFILES['WORKER'],
            'profile_url': reverse('worker', kwargs = {'user_id': worker.id}),
            'profile_icon': PROFILES_ICON_DIR + systemuser.icon_path,
            'systemuser': systemuser,
            'object_list': TestManager.list_all(),
        }
        
        return render(req, self.template_name, context)

###########################################

class TestAddView(PermissionRequiredMixin, View):
    permission_required = ('backend.add_test')

    def post(self, req:HttpRequest):
        params = req.POST
        
        # create and store a new test
        Test.objects.create(
            patientCI = params.get('ci'),
            testID = params.get('id'),
            type = params.get('type'),
            begin_date = datetime.utcnow
        ).save()
        
        # return back to test list
        return redirect('tests')

###########################################

class TestResolveView(PermissionRequiredMixin, View):
    permission_required = ('backend.edit_test')
    
    def post(self, req:HttpRequest):
        params = req.POST
        query_message = None
        
        # get identified test
        test = TestManager.get_test(params.get('id'))
        
        # update test state
        if test is not None:
            test.state = 'resolved'
            test.result = params.get('result')
            test.save()                
            query_message = 'STORE_CHANGES'    
        else:
            query_message = f'ERROR_UPDATING TEST id: { params.get("id") }'
        
        # return back to test list
        return redirect(reverse('tests')+'?'+urlencode({ 'query_message':query_message }))

# VISUAL ##############################################################################

class ResultListView(PermissionRequiredMixin, ListView):
    template_name = 'result_list.html'
    permission_required = ('backend.view_test')
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

# VISUAL ##############################################################################

class EventListView(PermissionRequiredMixin, ListView):
    query_message = ""
    template_name = 'event_list.html'
    permission_required = ('backend.edit_systemevent')
  
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

