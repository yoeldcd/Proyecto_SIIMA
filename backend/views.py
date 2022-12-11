
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


###############################################################################

class AuthView(View):
    
    def get(self, req:HttpRequest):
        query_message = ""
        authenticated = False
        response = {}
        
        state = SystemUserManager.authenticate_user(req, req.GET, response)
        
        # check authentication state
        if state == UNREGISTRED_USER:
            query_message = f'ERROR: Usuario no registrado'
        
        elif state == INVALID_CREDENTIAL:
            query_message = f'ERROR: Credenciales invalidas'
        
        else:
            # state is SUCCESS:
            authenticated = True
        
        # check authentication
        if authenticated:
            system_user = response['system_user']
            
            # go to profile role page type
            if system_user.system_role == 'admin' or system_user.system_role == 'worker':
                return redirect(reverse('worker'))
            else:
                return redirect(reverse('patient'))

        else:
            
            # go back to login
            return redirect(reverse('login')+'?'+urlencode({
                'query_message':query_message 
            }))

# VISUAL ##############################################################################

class LoginView(FormView):
    template_name = 'login.html'
    
    def get(self, req:HttpRequest):
        query_message = req.GET.get('query_message')
        
        if req.user.is_authenticated:
            SystemUserManager.deauthenticate_user(req)
            query_message = f'{ req.user.username } HA SALIDO DEL SISTEMA'
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
        }
        
        # renderize loguin form view page
        return render(req, self.template_name, context)

### PATIENT MANAGEMENT VIEWS ##########################################################

class SiginPatientView(View):
    
    def post(self, req:HttpRequest):
        query_message = ""
        params = req.POST
        response = {'new_user': None}
        signed = False
        
        # registre new patient user
        system_user = SystemUserManager.get_system_user(req.user)
        state = PatientManager.create_patient_user(system_user, params, response)
        
        # check registration state
        if state == INVALID_CREDENTIAL:
            query_message = 'ERROR: Duplicated profile credential'
        else:
            query_message = 'SUCESS: Patient Profile Registred'
            signed = True
        
        # execute redirections
        if req.user.is_authenticated:
            # go back to patient list
            return redirect(reverse('patients')+'?'+urlencode({
                'query_message': query_message 
            }))
        
        elif signed:
            # authenticate automatically a new patient
            return redirect(reverse('auth')+'?'+urlencode({
                'username': params.get('username'),
                'password': params.get('password'),
                'query_message': query_message 
            }))
        
        else:
            # go back to loguin
            return redirect(reverse('login')+'?'+urlencode({
            'query_message': query_message 
            }))

##################################################

class SignoutPatientView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_patient_profile')
    
    def get(self, req:HttpRequest, user_id : int):
        q_params = req.GET
        query_message = ""
        supressed = False
        response = {'supressed_patient': None }
        
        # try to supress profile
        system_user = SystemUserManager.get_system_user(req.user)
        state = PatientManager.supress_patient_user(system_user, user_id, q_params, response)
        
        # check supression state
        if state == UNREGISTRED_USER:
            query_message = "ERROR: El perfil no esta registrado"
        
        elif state == ERROR:
            query_message = "ERROR: No pudimos eliminar el perfil REINTENTALO LUEGO"
        
        else: # state is SUCCESS:
            query_message = "SUCCESS: Patient profile supressed"
            supressed = True
        
        # Make redirections    
        if system_user.system_role == 'admin':
            # go back to worker list
            return redirect(reverse('patients')+'?'+urlencode({
                'query_message': query_message 
            })) 
        elif system_user.system_role == 'patient':
            # go back to patient profile
            return redirect(reverse_lazy('patient', kargs = {'userID': system_user.id })+'?'+urlencode({
                'query_message': query_message 
            }))
        else:
            # go back to forbiden
            return redirect(reverse('forbiden')+'?'+urlencode({
                'query_message': query_message 
            }))
        
# VISUAL #########################################

class PatientProfileView(PermissionRequiredMixin, DetailView):
    template_name = 'patient_profile.html'
    permission_required = ('backend.view_patient_profile')
    
    def get(self, req:HttpRequest):
        
        # get logged patient profile  
        system_patient = PatientManager.get_registred_patient_user(req.user)
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_patient,
            'detailed_patient': system_patient
        }
        
        # render patient profile details view page
        return render(req, self.template_name, context)

# VISUAL #########################################

class EditPatientView(PermissionRequiredMixin, FormView):
    template_name = 'edit_patient.html'
    permission_required = ('backend.change_patient_profile')
    
    def get(self, req:HttpRequest, user_id:int):
        q_params = req.GET
        query_message = q_params.get('query_message')
        response = {'patient': None}
        exists_profile = False
        
        ### try to get edited profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = PatientManager.get_patient_user_by_id(user_id, response)
        
        ### check user registration ###
        
        if state == UNREGISTRED_USER:
            query_message = 'ERROR: Paciente no registrado'
            
        else:
            query_message = None
            exists_profile = True
        
        ### make HTTPResponse ###
        
        if not exists_profile:
            
            if system_user.system_role == 'admin':
                # go back to patient list
                return redirect(reverse('patients')+'?'+urlencode({
                    'query_message': query_message 
                }))
                
            elif system_user.system_role == 'worker':
                # go back to worker profile
                return redirect(reverse('worker')+'?'+urlencode({
                    'query_message': query_message 
                }))
            elif system_user.system_role == 'patient':
                # go back to patient profile
                return redirect(reverse_lazy('patient')+'?'+urlencode({
                    'query_message': query_message 
                }))
            else:
                # go back to forbin
                return redirect(reverse('forviden')+'?'+urlencode({
                    'query_message': query_message 
                }))
                
        else:
            
            # define context values
            context = {
                'current_time': datetime.now,
                'query_message': query_message,
                'system_user': system_user,
                'edited_patient': response['patient']
            }
            
            # renderize patient edition view page
            return render(req, self.template_name, context)

##################################################

class UpdatePatientView(PermissionRequiredMixin, UpdateView):
    permission_required = ('backend.change_patient_profile')
    
    def post(self, req:HttpRequest, user_id:int):
        q_params = req.POST
        query_message = q_params.get('query_message')
        response = {'patient': None}
        profile_updated = False
        
        ### try to update edited profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = PatientManager.update_patient_user_by_id(req, system_user, user_id, q_params, response)
        
        ### check user registration ###
        
        if state == UNREGISTRED_USER:
            query_message = 'ERROR: Paciente no registrado'
            
        if state == DUPLICATED_PROFILE:
            query_message = 'ERROR: Datos de perfil duplicados'
            
        else:
            query_message = 'SUCESS: Perfil de Actualizado'
            profile_updated = True
        
        ### make HTTPResponse ###
        
        if system_user.system_role == 'admin':
            # go back to patient list
            return redirect(reverse('patients')+'?'+urlencode({
                'query_message': query_message 
            }))
            
        elif system_user.system_role == 'worker':
            # go back to worker profile
            return redirect(reverse('worker')+'?'+urlencode({
                'query_message': query_message 
            }))
            
        elif system_user.system_role == 'patient':
            # go back to patient profile
            return redirect(reverse('patient')+'?'+urlencode({
                'query_message': query_message 
            }))
            
        else:
            # go back to forbiden
            return redirect(reverse('forbiden')+'?'+urlencode({
                'query_message': query_message 
            }))

# VISUAL #########################################

class PatientListView(PermissionRequiredMixin, ListView):
    template_name = 'patient_list.html'
    permission_required = ('backend.view_patient_list')
    
    def get(self, req:HttpRequest):
        response = {}
        query_message = req.GET.get('query_message')
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        object_list = PatientManager.list_all()
        
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            'object_list': object_list
        }
        
        EventManager.log_user_event(system_user, 'LOG','PATIENT LIST ACCESSED',f'El { system_user.system_role } {system_user.username} accedio a la lista de pacientes')
        
        # renderize patient list view page
        return render(req, self.template_name, context)



### WORKER MANAGEMENT VIEWS ###########################################################

class SiginWorkerView(View):
    permission_required = ('backend.create_worker_profile')
    
    def post(self, req:HttpRequest):
        query_message = ""
        params = req.POST
        response = {'worker': None}
        
        # try to registre new worker user
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.create_worker_user(system_user, params, response)
        
        # check registration state
        if state == INVALID_CREDENTIAL:
            query_message = 'ERROR: Duplicated profile credential'
        else:
            query_message = 'SUCESS: Worker Profile Registred'
        
        # execute redirections
        if system_user.system_role == 'admin':
            # go back to worker list
            return redirect(reverse('workers')+'?'+urlencode({
                'query_message': query_message 
            }))
        else:
            # go back to loguin
            return redirect(reverse('login')+'?'+urlencode({
                'query_message': query_message 
            }))

##################################################

class SignoutWorkerView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_worker_profile')
    
    def get(self, req:HttpRequest, user_id:int):
        q_params = req.GET
        query_message = ""
        response = {'worker': None }
        supressed = False
        
        ### try to supress profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.supress_worker_user_by_id(system_user, user_id, q_params, response)
        
        ### check supression state ###
        
        if state == UNREGISTRED_USER:
            query_message = "ERROR: El perfil no esta registrado"
        
        elif state == ERROR:
            query_message = "ERROR: No pudimos eliminar el perfil REINTENTALO LUEGO"
        
        else: # state is SUCCESS:
            query_message = "SUCCESS: Perfil eliminado"
            supressed = True
        
        ### Make HTTP Response ###
            
        if system_user.system_role == 'admin':
            # go back to worker list
            return redirect(reverse('workers')+'?'+urlencode({
                'query_message': query_message 
            })) 
        else:
            # go back to forbiden
            return redirect(reverse('forbiden')+'?'+urlencode({
                'query_message': query_message 
            }))

# VISUAL #########################################

class WorkerProfileView(PermissionRequiredMixin, DetailView):
    template_name = 'worker_profile.html'
    permission_required = ('backend.view_worker_profile')
    
    def get(self, req:HttpRequest):
        
        # get logged worker profile 
        system_worker = WorkerManager.get_registred_worker_user(req.user)
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': req.GET.get('query_message'),
            'system_user': system_worker,
            'detailed_worker': system_worker
        }
        
        # render worker profile details view page
        return render(req, self.template_name, context)

# VISUAL #########################################

class EditWorkerView(PermissionRequiredMixin, FormView):
    template_name = 'edit_worker.html'
    permission_required = ('backend.change_worker_profile')
    
    def get(self, req:HttpRequest, user_id:int):
        q_params = req.GET
        query_message = q_params.get('query_message')
        response = {'worker': None}
        exists_profile = False
        
        ### try to get edited worker profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.get_worker_user_by_id(user_id, response)
        
        ### check user registration ###
        
        if state == UNREGISTRED_USER:
            query_message = 'ERROR: Perfil no registrado'
            
        else:
            query_message = None
            exists_profile = True
        
        ### Make HTTP Response ###
        
        if not exists_profile:
            
            if system_user.system_role == 'admin':
                # go back to worker list
                return redirect(reverse('workers')+'?'+urlencode({
                    'query_message': query_message 
                }))
                
            elif system_user.system_role == 'worker':
                # go back to worker profile
                return redirect(reverse('worker')+'?'+urlencode({
                    'query_message': query_message 
                }))
                
            else:
                # go back to forbin
                return redirect(reverse('forbiden')+'?'+urlencode({
                    'query_message': query_message 
                }))
                
        else:
            
            # define context values
            context = {
                'current_time': datetime.now,
                'query_message': query_message,
                'system_user': system_user,
                'edited_worker': response['worker']
            }
            
            # renderize worker edition view page
            return render(req, self.template_name, context)

##################################################

class UpdateWorkerView(PermissionRequiredMixin, UpdateView):
    permission_required = ('backend.change_worker_profile')
    
    def post(self, req:HttpRequest, user_id:int):
        q_params = req.POST
        query_message = q_params.get('query_message')
        response = {'worker': None}
        profile_updated = False
        
        ### Try to update edited profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.update_worker_user_by_id(req, system_user, user_id, q_params, response)
        
        ### Check profile updates ###
        
        if state == UNREGISTRED_USER:
            query_message = 'ERROR: Trabajador no registrado'
            
        if state == DUPLICATED_PROFILE:
            query_message = 'ERROR: Datos de perfil duplicados'
            
        else:
            query_message = 'SUCESS: Perfil del Trabajador Actualizado'
            profile_updated = True
        
        ### Make HTTP Response ###
        
        if system_user.system_role == 'admin':
            # go back to worker list
            return redirect(reverse('workers')+'?'+urlencode({
                'query_message': query_message 
            }))
        elif system_user.system_role == 'worker':
            # go back to worker profile
            return redirect(reverse('worker')+'?'+urlencode({
                'query_message': query_message 
            }))
        else:
            # go back to forbiden
            return redirect(reverse('forbiden')+'?'+urlencode({
                'query_message': query_message 
            }))

# VISUAL #########################################

class WorkerListView(PermissionRequiredMixin, ListView):
    template_name = 'worker_list.html'
    permission_required = ('backend.view_worker_list')
    
    def get(self, req:HttpRequest):
        response = {}
        query_message = req.GET.get('query_message')
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        object_list = WorkerManager.list_all()
        
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            'object_list': object_list
        }
        
        # renderize list view page
        return render(req, self.template_name, context)



### TEST'S MANAGEMENT VIEWS ###########################################################

class AddTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.create_test')
    
    def post(self, req:HttpRequest):
        params = req.POST
        query_message = ''
        response = {'test': None}
        
        ### Try to create a new test on DB ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.create_test(system_user, params, response)
        
        ### Check test creation state ###
        
        if state == DUPLICATED_INSTANCE:
            query_message = 'ERROR: No se pudo crear el analisis porque el id ya esta siendo utilizado por otro en proceso, CAMBIELO E INTENTELO DE NUEVEO'
        
            
        if state == INTERNAL_ERROR:
            query_message = 'ERROR: No se pudo crear el analisis por un ERROR interno, INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS: El nuevo analisis fue agregado'
        
        ### make HTTP Response ###
        
        # go back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message': query_message
        }))

##################################################

class ResolveTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.resolve_test')
    
    def post(self, req:HttpRequest, test_id):
        params = req.POST
        query_message = ''
        response = {'test': None}
        
        ### Try to update test associted to ID ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.update_test_by_id(system_user, test_id, params, response)
        
        ### Check test update state ###
        
        if state == INTERNAL_ERROR:
            query_message = 'ERROR: No se pudo actualizar el resultado por un ERROR interno, INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS: El analisis fue actualizado'
        
        ### make HTTP Response ###
        
        # go back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message': query_message
        }))

##################################################

class NotifyTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.notify_test')
    
    def get(self, req:HttpRequest, test_id):
        params = req.POST
        query_message = ''
        response = {'test': None}
        
        ### Try to notify test associted to ID ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.notify_test_by_id(system_user, test_id, params, response)
        
        ### Check test notification state ###
        
        if state == INTERNAL_ERROR:
            query_message = 'ERROR: No se pudo enviar el analisis por un ERROR interno, INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS: El analisis fue enviado al paciente'
        
        ### make HTTP Response ###
        
        # go back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message': query_message
        }))
        
# VISUAL ##########################################

class TestListView(PermissionRequiredMixin, ListView):
    template_name = 'test_list.html'
    permission_required = ('backend.view_test_list')
    
    def get(self, req:HttpRequest):
        q_params = req.GET
        query_message = q_params['query_message']
        
        # get logged user profile
        system_user = SystemUserManager.get_registred_system_user(req.user)
        object_list = TestManager.list_all_unnotified_tests(q_params)
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            'object_list': object_list,
        }
        
        # renderize test list view
        return render(req, self.template_name, context)



### RESULTS MANAGEMENT VIEWS ##########################################################


class SupressResultView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_result')
    
    def get(self, req:HttpRequest, test_id):
        params = req.POST
        query_message = ''
        response = {'test': None}
        
        ### Try to notify test associted to ID ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.delete_test_by_id(system_user, test_id, response)
        
        ### Check test supression state ###
        
        if state == INTERNAL_ERROR:
            query_message = 'ERROR: No se pudo eliminar el analisis por un ERROR interno, INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS: El analisis fue eliminado'
        
        ### make HTTP Response ###
        
        # go back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message': query_message
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


# VISUAL ##############################################################################

class EventListView(PermissionRequiredMixin, ListView):
    
    query_message = ""
    template_name = 'event_list.html'
    permission_required = ('backend.view_event_list')
    
    def get(self, req:HttpRequest):
        
        q_params = req.GET
        query_message = q_params.get('query_message')
        
        # get loggued admin profile
        system_user = SystemUserManager.get_registred_system_user(req.user)
        detailed_user = None
        object_list = None
        response = {'user': None, 'object_list': None }
        
        ### Get detailed events user profile asocited to ID from DB ###
        
        state = EventManager.list_all_events(q_params, response)
        
        ### Check event fetch state ###
            
        if state == INTERNAL_ERROR:
            query_message = 'ERROR: No se pudo acceder a los eventos del perfil por un ERROR interno, INTENTELO DE NUEVO'
        
        if state == UNREGISTRED_INSTANCE:
            query_message = 'ERROR: Usuario no registrado'

        else:
            # get response events associeted to profile
            detailed_user = response['user']
            object_list = response['object_list']
            
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            'detailed_user': detailed_user,
            'object_list': object_list
        }
        
        # renderize profile event list view page
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

