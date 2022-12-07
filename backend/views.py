
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


# VISUAL ##############################################################################

class LoginView(FormView):
    template_name = 'login.html'
    
    def get(self, req:HttpRequest):
        query_message = req.GET.get('query_message')
        
        # logout current user
        if req.user.is_authenticated:
            query_message = f'{ req.user.username } HA SALIDO DEL SISTEMA'
            EventManager.log_user_event(req.user,'LOG','USER LOGGOUT',f'User {req.user.username} cerro su sesion ')
            logout(req)
            
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
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

            # log action
            EventManager.log_system_event('WARNING','AUTHENTICATION FAIL',f'User {username} intento iniciar sesion con password {password}')
            query_message = f'ERROR: Credenciales invalidas'

            return redirect(reverse('login')+'?'+urlencode({
                'query_message':query_message 
            }))
        
        # start new user sesion
        login(req, user)
        system_user = SystemUserManager.get_system_user(user)
        
        # log action
        EventManager.log_user_event(system_user, 'LOG','AUTHENTICATION',f'El usuario { system_user.username } inicio su sesion con rol { system_user.system_role }')
            
        # select profile page type
        if system_user.system_role == 'admin' or system_user.system_role == 'worker':
            return redirect('/worker/'+str(system_user.id))
        else:
            return redirect('/patient/'+str(system_user.id))

# VISUAL ##############################################################################

class PatientProfileView(PermissionRequiredMixin, DetailView):
    template_name = 'patient_profile.html'
    permission_required = ('backend.view_patient_profile')
    
    def get(self, req:HttpRequest, user_id:int):
        
        system_patient = PatientManager.get_patient_user(req.user)
        print(system_patient)
        

        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_patient,
            'detailed_patient': system_patient
        }
        
        return render(req, self.template_name, context)

###########################################

class SiginPatientView(View):
    
    def post(self, req:HttpRequest):
        query_message = ""
        params = req.POST
        
        # registre new patient user
        new_patient = PatientManager.create_patient_user(params)
        
        if  not req.user.is_authenticated :
            # redirect admin to profile_page
            query_message = "SUCESS: Welcome: " + params.get('username')
            
            # log action
            username = params.get('username')
            EventManager.log_user_event(req.user, 'LOG', 'PROFILE ADDED',f'El paciente { username } se registro en la BD')
        
            return redirect('/auth?'+urlencode({
                'username': params.get('username'),
                'password': params.get('password'),
                'query_message': query_message 
            }))
        elif req.user.is_superuser:
            query_message = "SUCESS: Patient Profile Registred: " + params.get('username') + " PASSWORD " + params.get('password')
            
            # log action
            username = params.get('username')
            EventManager.log_user_event(req.user, 'LOG', 'PROFILE ADDED',f'El admin {req.user.username} regristro al paciente { username } en la BD')
            
            return redirect('/patients?'+urlencode({
                'query_message': query_message 
            }))

class SignoutPatientView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_patient_profile')

    def get(self, req:HttpRequest, user_id : int):
        query_message = ""
        
        # get patient profile to supress
        supressed_patient = PatientManager.get_patient_user_by_id(user_id)
        
        if supressed_patient is None:
            query_message = "ERROR: No identified patient"
        else:
            # supress profile from DB
            PatientManager.supress_patient_user(supressed_patient)
            query_message = "SUCCESS: Patient profile supressed"
        
        if req.user.is_superuser:
            # log action
            username = supressed_patient.username
            EventManager.log_user_event(req.user, 'WARNING', 'PROFILE SUPRESSED',f'El admin {req.user.username} suprimio el perfil del paciente { username } en la BD')
            
            # go back to worker list
            return redirect(reverse('patients')+'?'+urlencode({
                'query_message': query_message 
            }))
        else:
            username = supressed_patient.username
            EventManager.log_user_event(req.user,'WARNING', 'PROFILE SUPRESSED',f'El paciente {username} suprimio su perfil en la BD')
        
        # go back to login
        return redirect(reverse('loguin')+'?'+urlencode({
            'query_message': query_message 
        }))

# VISUAL ##########################################

class EditPatientView(PermissionRequiredMixin, FormView):
    template_name = 'edit_patient.html'
    permission_required = ('backend.change_patient_profile')
    
    def get(self, req:HttpRequest, user_id):
        q_params = req.GET
        query_message = q_params.get('query_message')
        
        system_user = SystemUserManager.get_system_user(req.user)
        edited_patient = PatientManager.get_patient_user_by_id(user_id)
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            'edited_patient': edited_patient
        }
        
        return render(req, self.template_name, context)
    
    def post(self, req: HttpRequest, user_id : int):
        q_params = req.POST
        query_message = ""
        
        # check patient joined
        edited_patient = PatientManager.get_patient_user_by_id(user_id)
        
        if edited_patient is None:
            query_message = "ERROR No identified patient"
            return redirect(reverse('workers')+urlencode({
                'query_message': query_message
            }))
        
        # update patient profile
        PatientManager.update_patient_user(edited_patient, q_params)
        query_message = "SUCCESS: Pateint profile updated"
        
        if req.user.is_superuser:
            EventManager.log_user_event(req.user, 'WARNING','PATIENT PROFILE MODIFIED',f'El admin { req.user.username} modifico los datos en el perfil del paciente { edited_patient.username }')
            
            return redirect('/patients?'+urlencode({
                'query_message': query_message
            }))
            
        else:
            EventManager.log_user_event(req.user, 'WARNING','PATIENT PROFILE MODIFIED',f'El  paciente { edited_patient.username } modifico los datos de su perfil')
            
            # go back to patient profile page
            return redirect(f'/patient/{req.user.id}?'+urlencode({
                'query_message': query_message
            }))

# VISUAL ##########################################

class PatientListView(PermissionRequiredMixin, ListView):
    template_name = 'patient_list.html'
    permission_required = ('backend.view_patient_list')
    
    def get(self, req:HttpRequest):
        
        system_user = SystemUserManager.get_system_user(req.user)
        
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_user,
            'object_list': PatientManager.list_all() 
        }
        
        EventManager.log_user_event(system_user, 'LOG','PATIENT LIST ACCESSED',f'El { system_user.system_role } {system_user.username} accedio a la lista de pacientes')
        return render(req, self.template_name, context)

# VISUAL ##############################################################################

class WorkerProfileView(PermissionRequiredMixin, DetailView):
    template_name = 'worker_profile.html'
    permission_required = ('backend.view_worker_profile')
    
    def get(self, req:HttpRequest, user_id:int):
        
        system_worker = WorkerManager.get_worker_user(req.user)
        print(system_worker)
        
        # define context values from template rendering
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_worker,
            'detailed_worker': system_worker
        }
        
        return render(req, self.template_name, context)

###########################################

class SiginWorkerView(View):
    permission_required = ('backend.create_worker_profile')
    
    def post(self, req:HttpRequest):
        params = req.POST
        
        # registre new worker user
        worker = WorkerManager.create_worker_user(params)
        query_message = "SUCCESS: Worker Profile Registred: " + params.get('username') + " PASSWORD " + params.get('password')
        
        # log action
        username = params.get('username')
        EventManager.log_user_event('LOG', 'PROFILE ADDED',f'El admin {req.user.username} regristro al especialista { username } en la BD')
        
        # redirect admin to worker list
        return redirect(reverse('workers')+'?'+urlencode({
            'query_message': query_message 
        }))

class SignoutWorkerView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_worker_profile')
    
    def get(self, req:HttpRequest, user_id : int):
        query_message = ""
        
        # get worker profile to supress
        supressed_worker = WorkerManager.get_worker_user_by_id(user_id)
        
        if supressed_worker is None:
            query_message = "ERROR: No identified worker"
        else:
            # supress profile from DB
            WorkerManager.supress_worker_user(supressed_worker)
            query_message = "SUCCESS: Worker profile supressed"
        
        # log action
        username = supressed_worker.username
        EventManager.log_user_event('WARNING', 'PROFILE SUPRESSED',f'El admin {req.user.username} regristro suprimio el perfil de { username } en la BD')
        
        # go back to worker list
        return redirect(reverse('workers')+'?'+urlencode({
            'query_message': query_message 
        }))

# VISUAL ##########################################

class EditWorkerView(PermissionRequiredMixin, FormView):
    template_name = 'edit_worker.html'
    permission_required = ('backend.change_worker_profile')
    
    def get(self, req:HttpRequest, user_id):
        q_params = req.GET
        query_message = q_params.get('query_message')
        
        system_user = SystemUserManager.get_system_user(req.user)
        edited_worker = WorkerManager.get_worker_user_by_id(user_id)
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            'edited_worker': edited_worker
        }
        
        print(edited_worker.user_permissions)
        
        return render(req, self.template_name, context)
    
    def post(self, req: HttpRequest, user_id : int):
        q_params = req.POST
        query_message = ""
        
        # check worker joined
        edited_worker = WorkerManager.get_worker_user_by_id(user_id)
        
        if edited_worker is None:
            query_message = "ERROR: No identified worker to update"
            return redirect(f'/worker/{req.user.id}?'+urlencode({
                'query_message': query_message
            }))
        
        
        # restrict permission asignement policies (admin_only, not_current_admin)
        can_revoke_permissions = q_params.get('admin_password') == 'root@6267' and req.user.is_superuser and edited_worker.id != req.user.id
        
        # update worker profile
        WorkerManager.update_worker_user(edited_worker, q_params, can_revoke_permissions)
        query_message = f"SUCESS: Worker profile { edited_worker.username } updated,"
        
        if can_revoke_permissions:
            query_message += "PERMISSIONS CHANGED"
        
            
        if req.user.is_superuser:
            # go back to worker list
            EventManager.log_user_event(req.user, 'WARNING','WORKER PROFILE MODIFIED',f'El admin { req.user.username} modifico los datos en el perfil del especialista { edited_worker.username }')
            
            return redirect('/workers?'+urlencode({
                'query_message': query_message
            }))
        else:
            # go back to profile view
            EventManager.log_user_event(req.user, 'WARNING','WORKER PROFILE MODIFIED',f'El worker { edited_worker.username} modifico los datos en su perfil')
            
            return redirect(f'/worker/{req.user.id}?'+urlencode({
                'query_message': query_message
            }))
    
# VISUAL ##########################################

class WorkerListView(PermissionRequiredMixin, ListView):
    template_name = 'worker_list.html'
    permission_required = ('backend.view_worker_list')
     
    def get(self, req:HttpRequest):
        
        system_user = SystemUserManager.get_system_user(req.user)
        
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_user,
            'object_list': WorkerManager.list_all() 
        }
        
        EventManager.log_user_event(system_user, 'LOG','WORKER LIST ACCESSED',f'El { system_user.system_role } {system_user.username} accedio a la lista de especialistas')
        return render(req, self.template_name, context)

# VISUAL ##############################################################################

class TestListView(PermissionRequiredMixin, ListView):
    template_name = 'test_list.html'
    permission_required = ('backend.view_test_list')
    
    def get(self, req:HttpRequest):
        system_user = SystemUserManager.get_system_user(req.user)
        object_list = TestManager.list_all_unnotified_tests()

        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_user,
            'object_list': object_list,
        }
        
        return render(req, self.template_name, context)

###########################################

class AddTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.create_test')
    
    def post(self, req:HttpRequest):
        query_message = "CREATED: New Test"
        params = req.POST
        
        # create a new test on model
        TestManager.add_test(params)
        
        # return back to test list
        EventManager.log_user_event(req.user, 'LOG','NEW TEST ADDED',f'El ususraio { req.user.username} registro un nuevo analisis en la BD')
        return redirect(f'/tests/?query_message="{ query_message }"')

###########################################

class ResolveTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.resolve_test')
    
    def post(self, req:HttpRequest, test_id):
        params = req.POST
        query_message = req.POST.get('query_message')
        
        # get identified test
        resolved_test = TestManager.get_test_by_id(test_id)
        
        # check test on DB
        if resolved_test is None:
            EventManager.log_user_event(req.user, 'WARNING','TEST MODIFIED FAIL',f'El ususraio { req.user.username} inteto modificar un analisis no registrado en la BD')
            query_message = f'ERROR: No identified Test : { params.get("id") }'
        else:
            # update test with result
            EventManager.log_user_event(req.user, 'LOG','TEST MODIFIED',f'El ususraio { req.user.username} modifico un analisis en la BD')
            TestManager.resolve_test(resolved_test, params.get('result'))
            query_message = 'STORE_CHANGES'

        # return back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message':query_message
        }))

###########################################

class NotifyTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.notify_test')
    
    def get(self, req:HttpRequest, test_id):
        params = req.GET
        query_message = params.get('query_message')
        
        # get identified test
        notified_test = TestManager.get_test_by_id(test_id)
        
        # check test on DB
        if notified_test is None:
            EventManager.log_user_event(req.user, 'WARNING','TEST NOTIFIED FAIL',f'El ususraio { req.user.username} inteto notificar un analisis no registrado en la BD')
            query_message = f'ERROR: No identified Test : { params.get("id") }'
        else:
            # update test with result
            TestManager.notify_test(notified_test)
            
            # log action
            EventManager.log_user_event(req.user, 'LOG','TEST NOTIFIED',f'El ususraio { req.user.username} notifico un analisis en la BD')
            query_message = 'SUCESS: Test sended'
        
        # return back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message':query_message
        }))

# VISUAL ##############################################################################

class ResultListView(PermissionRequiredMixin, ListView):
    template_name = 'result_list.html'
    permission_required = ('backend.view_result_list')
    
    def get(self, req:HttpRequest):
        query_message = req.GET
        system_patient = PatientManager.get_patient_user(req.user)
        
        if system_patient is None:
            query_message = 'ERROR: No identified patient'
        
        # get a list of test asociateds to patient
        object_list = TestManager.list_all_patient_tests(system_patient)
        
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_patient,
            'object_list': object_list,
        }
        
        return render(req, self.template_name, context)

class SupressResultView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_result')
    
    def get(self, req:HttpRequest, test_id):
        params = req.GET
        query_message = params.get('query_message')
        
        # get identified test
        supressed_test = TestManager.get_test_by_id(test_id)
        
        # check test on DB
        if supressed_test is None:
            EventManager.log_user_event(req.user, 'WARNING','TEST SUPRESSION FAIL',f'El ususraio { req.user.username} inteto eliminar un analisis no registrado en la BD')
            query_message = f'ERROR: No identified Test : { params.get("id") }'
        else:
            # update test with result
            TestManager.delete_test(supressed_test)
            
            # log action
            EventManager.log_user_event(req.user, 'WARNING','TEST SUPRESSED',f'El ususraio { req.user.username} elimino un analisis en la BD')
            query_message = 'SUCESS: Test delete'
        
        # return back to test list
        return redirect(reverse('results')+'?'+urlencode({
            'query_message':query_message
        }))

# VISUAL ##############################################################################

class EventListView(PermissionRequiredMixin, ListView):
    
    query_message = ""
    template_name = 'event_list.html'
    permission_required = ('backend.view_event_list')
    
    def get(self, req:HttpRequest):
        
        params = req.GET
        query_message = params.get('query_message')
        system_user = SystemUserManager.get_system_user(req.user)
        
        if 'user_id' in params:
            systemuser = SystemUserManager.get_system_user_by_id(params.get('user_id'))
            
            if systemuser is None:
                query_message = f'ERROR: No registred user'
                user_id = params.get('user_id')
                EventManager.log_user_event(system_user, 'DANGER', 'PROFILE EVENTS FAIL', f'El {system_user.system_role} { system_user.username } intento acceder a los datos del usuario no registrado {user_id}')
            
            object_list = EventManager.list_all_user_events(systemuser)
        else:
            object_list = EventManager.list_all_events()
        
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            'object_list': object_list 
        }
        
        return render(req, self.template_name, context)

class SupressEventView(PermissionRequiredMixin, View):
    
    query_message = ""
    template_name = 'event_list.html'
    permission_required = ('backend.delete_event')

    def get(self, req, event_id):
        query_message = ''

        # delete log of DB model 
        if EventManager.supress_event_by_id(event_id):
            query_message = 'SUCESS: Event Log deleted'
        else:
            query_message = 'ERROR: Event Log not deleted'
        
        return redirect('/events/?'+urlencode({
            'query_message': query_message
        }))

