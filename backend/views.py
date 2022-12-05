
from datetime import datetime

from django.utils.http import urlencode
from django.http import HttpRequest, HttpResponse;
from django.shortcuts import render, redirect;
from django.views.generic import *;
from django.contrib.auth import *;
from django.urls import *

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

class PatientProfileView(DetailView):
    template_name = 'patient_profile.html'
    
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

        query_message = "REGISTRED USER: " + params.get('username') + " PASSWORD " + params.get('password')
        
        # redirect admin to profile_page
        return redirect(reverse('auth')+'?'+urlencode({
            'username': params.get('username'),
            'password': params.get('password'),
            'query_message': query_message 
        }))

# VISUAL ##########################################

class EditPatientView(FormView):
    template_name = 'edit_patient.html'
    
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
            'profile_url': reverse('worker', kwargs = {'user_id': req.user.id }),
            'profile_icon': PROFILES_ICON_DIR + systemuser.icon_path,
            'systemuser': systemuser,
            'edited_patient': edited_patient
        }
        
        if systemuser.is_superuser:
            context['profile_type'] = PROFILES['ADMIN']
        
        return render(req, self.template_name, context)

    def post(self, req: HttpRequest, user_id : int):
        q_params = req.POST
        query_message = ""
        
        edited_patient = PatientManager.get_patient_user_by_id(user_id)
        
        if edited_patient is None:
            query_message = "ERROR No identified patient"
            return redirect(reverse('workers')+urlencode({'query_message': query_message}))
        
        # update patient with new field values
        field = 'username'
        if q_params.get(field) != '':
            edited_patient.username = q_params.get(field)
        
        field = 'password'
        if q_params.get(field) != '':
            edited_patient.password = q_params.get(field)
        
        field = 'email'
        if q_params.get(field) != '':
            edited_patient.email = q_params.get(field)
        
        field = 'ci'
        if q_params.get(field) != '':
            edited_patient.ci = q_params.get(field)
        
        field = 'first_name'
        if q_params.get(field) != '':
            edited_patient.first_name = q_params.get(field)
            
        field = 'last_name'
        if q_params.get(field) != '':
            edited_patient.last_name = q_params.get(field)
            
        field = 'sex'
        if q_params.get(field) != '':
            edited_patient.sex = q_params.get(field)
            
        field = 'age'
        if q_params.get(field) != '':
            edited_patient.age = int(q_params.get(field))
        
        field = 'phone'
        if q_params.get(field) != '':
            edited_patient.phone = q_params.get(field)
        
        if q_params.get('blod_group_letter') != '' and q_params.get('blod_group_letter') != '':
            edited_patient.blod_group = q_params.get('blod_group_letter') + q_params.get('blod_group_letter')
        
        # save updated patient 
        edited_patient.save()
        query_message = "SUCCESS: Pateint profile updated"
        
        # go back to patient list
        return redirect(reverse('patients')+'?'+urlencode({'query_message': query_message}))

# VISUAL ##########################################

class PatientListView(ListView):
    template_name = 'patient_list.html'
    
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

class WorkerProfileView(DetailView):
    template_name = 'worker_profile.html'
    
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

class SiginWorkerView(View):
    
    def post(self, req:HttpRequest):
        params = req.POST
        
        # registre new worker user
        worker = Worker.objects.create_user(
            username = params.get('username'),
            password = params.get('password'),
            email = params.get('email'),
            ci = params.get('ci'),
            first_name = params.get('first_name'),
            last_name = params.get('last_name'),
            sex = params.get('sex'),
            age = params.get('age'),
            phone = params.get('phone'),
            role = params.get('role')
        )
        
        # define super_user role
        if params['permission_root'] == 'true':
            worker.is_superuser = True
        
        worker.save()
        
        # redirect admin to worker list
        return redirect('workers')

# VISUAL ##########################################

class EditWorkerView(FormView):
    template_name = 'edit_worker.html'
    
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
        q_params = req.GET
        query_message = ""
        
        edited_worker = WorkerManager.get_worker_user_by_id(user_id)
        
        if edited_worker is None:
            query_message = "ERROR No identified worker"
            return redirect(reverse('workers')+urlencode({'query_message': query_message}))
        
        # update worker with new field values
        field = 'username'
        if q_params.get(field) != '':
            edited_worker.username = q_params.get(field)
        
        field = 'password'
        if q_params.get(field) != '':
            edited_worker.password = q_params.get(field)
        
        field = 'email'
        if q_params.get(field) != '':
            edited_worker.email = q_params.get(field)
        
        field = 'ci'
        if q_params.get(field) != '':
            edited_worker.ci = q_params.get(field)
        
        field = 'first_name'
        if q_params.get(field) != '':
            edited_worker.first_name = q_params.get(field)
            
        field = 'last_name'
        if q_params.get(field) != '':
            edited_worker.last_name = q_params.get(field)
            
        field = 'sex'
        if q_params.get(field) != '':
            edited_worker.sex = q_params.get(field)
            
        field = 'age'
        if q_params.get(field) != '':
            edited_worker.age = int(q_params.get(field))
        
        field = 'phone'
        if q_params.get(field) != '':
            edited_worker.phone = q_params.get(field)
        
        field = 'role'
        if q_params.get(field) != '':
            edited_worker.role = q_params.get(field)
        
        # updating permission
        
        
        # save updated worker

        edited_worker.save()
        query_message = "Worker profile updated"
        
        # go back to worker list
        return redirect(reverse('workers')+urlencode({'query_message': query_message}))
    
# VISUAL ##########################################

class WorkerListView(ListView):
    template_name = 'worker_list.html'
    
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

class TestListView(ListView):
    template_name = 'test_list.html'
    
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

class TestAddView(View):

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

class TestResolveView(View):
    
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

class ResultListView(ListView):
    template_name = 'result_list.html'
    
    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

# VISUAL ##############################################################################

class EventListView(ListView):
    query_message = ""
    template_name = 'event_list.html'
    
    

    def get(self, req:HttpRequest):
        return render(req, self.template_name, {})

