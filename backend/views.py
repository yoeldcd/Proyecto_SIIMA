
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
        
        response = dict()
        query_message = ""
        authenticated = False
        
        state = SystemUserManager.authenticate_user(req, req.GET, response)
        
        # check authentication state
        if state == UNREGISTRED_PROFILE:
            query_message = f'ERROR, Usuario no registrado, Para usar el sistema debe crear una cuenta'
        
        elif state == INVALID_CREDENTIAL:
            query_message = f'ERROR, Credenciales invalidas, verifique los datos introducidos e intentelo de nuevo'
        
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
            query_message = f'NOTICE, { req.user.username } HA SALIDO DEL SISTEMA'
            SystemUserManager.deauthenticate_user(req)
            
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
        }
        
        # renderize loguin form view page
        return render(req, self.template_name, context)

#
##
### PATIENT MANAGEMENT VIEWS ##########################################################

class SiginPatientView(View):
    
    def post(self, req:HttpRequest):
        
        params = copy_dict(req.POST)
        response = dict()
        query_message = ""
        signed = False
        
        # registre new patient user
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = PatientManager.create_patient_user(system_user, params, response)
        
        # check registration state
        if state == INVALID_CREDENTIAL:
            query_message = 'ERROR, Credenciales duplicadas, Sus credenciales de registros ya estan siendo usadas por otro usuario. Cambielas e intente el registro nuevamente'
        else:
            
            if system_user is None:
                query_message = 'SUCCESS, Su cuenta se creo satisfactoriamente'
            else:
                query_message = 'SUCCESS, Cuenta creada satisfactoriamente'
            
            signed = True
        
        # execute redirections
        if signed:
            if system_user is not None:
                # go back to patient list
                return redirect(reverse('patients')+'?'+urlencode({
                    'query_message': query_message 
                }))
        
            else:
                # authenticate automatically a new patient
                return redirect(reverse('auth')+'?'+urlencode({
                    'username': params.get('username'),
                    'password': params.get('password'),
                    'query_message': query_message 
                }))
            
        else:
            # go back to login
            return redirect(reverse('login')+'?'+urlencode({
                'query_message': query_message 
            }))

##################################################

class SignoutPatientView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_patient_profile')
    
    def get(self, req:HttpRequest, user_id : int):
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = ""
        
        # try to supress profile
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = PatientManager.supress_patient_user_by_id(system_user, user_id, q_params, response)
        
        # check supression state
        if state == UNREGISTRED_PROFILE:
            query_message = "ERROR, El perfil no esta registrado"
        
        elif state == ERROR:
            query_message = "ERROR, Perfil no eliminado, No pudimos eliminar el perfil por un error tecnico, intentelo de nuevo"
        
        else: # state is SUCCESS:
            query_message = "SUCCESS: Perfil eliminado satisfacoriamente"
            
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
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        exists_profile = False
        
        ### try to get edited profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = PatientManager.get_patient_user_by_id(user_id, response)
        
        ### check user registration ###
        
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Paciente no registrado'
            
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
        
        q_params = copy_dict(req.POST)
        response = dict()
        query_message = q_params.get('query_message')
        
        ### try to update edited profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = PatientManager.update_patient_user_by_id(req, system_user, user_id, q_params, response)
        
        ### check user registration ###
        
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Paciente no registrado'
            
        if state == DUPLICATED_PROFILE:
            query_message = 'ERROR, Datos de perfil duplicados, Los datos registrados ya estan siendo usadas por otro usuario. Cambielas e intente el registro nuevamente'
            
        else:
            query_message = 'SUCESS, Perfil de Actualizado satisfactoriamente'
            
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
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = PatientManager.filter_patients(q_params, response)
        
        # check query state
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Usuario no registrado'
        elif state == INTERNAL_ERROR:
            query_message = 'ERROR, Error de Lista, No pudimmos recuperar la lista de pacientes por problemas tecnicos. Intetelo de nuevo'
        
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            
            # list values
            'object_list': response.get('object_list'),
            'filtered_username': response.get('filtered_username'),
            'filter': response.get('filter'),
            'list_filters': 'username date'
        }
        
        EventManager.log(system_user,'PATIENT LIST ACCESSED',f'El { system_user.system_role } {system_user.username} accedio a la lista de pacientes')
        
        # renderize patient list view page
        return render(req, self.template_name, context)

#
##
### WORKER MANAGEMENT VIEWS ###########################################################

class SiginWorkerView(View):
    permission_required = ('backend.create_worker_profile')
    
    def post(self, req:HttpRequest):
        
        q_params = copy_dict(req.POST)
        response = dict()
        query_message = ""
        
        # try to registre new worker user
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.create_worker_user(system_user, q_params, response)
        
        # check registration state
        if state == INVALID_CREDENTIAL:
            query_message = 'ERROR, Credenciales duplicadas, Las credenciales de registros ya estan siendo usadas por otro usuario. Cambielas e intente el registro nuevamente'
        else:
            query_message = 'SUCESS, El perfil se creo satisfactoriamente'
        
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
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = ""
        
        ### try to supress profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.supress_worker_user_by_id(system_user, user_id, q_params, response)
        
        ### check supression state ###
        
        if state == UNREGISTRED_PROFILE:
            query_message = "ERROR, El perfil no esta registrado"
        
        elif state == ERROR:
            query_message = "ERROR, Perfil no eliminado, No pudimos eliminar el perfil por un problema tecnico"
        
        else: # state is SUCCESS:
            query_message = "SUCCESS, Perfil eliminado satisfactoramente"
            
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
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        exists_profile = False
        
        ### try to get edited worker profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.get_worker_user_by_id(user_id, response)
        
        ### check user registration ###
        
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Perfil no registrado'
            
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
        
        q_params = copy_dict(req.POST)
        response = dict()
        query_message = q_params.get('query_message')
        
        ### Try to update edited profile ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = WorkerManager.update_worker_user_by_id(req, system_user, user_id, q_params, response)
        
        ### Check profile updates ###
        
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Trabajador no registrado'
            
        if state == DUPLICATED_PROFILE:
            query_message = 'ERROR, Datos de perfil duplicados, Las credenciales registradas ya estan siendo usadas por otro usuario. Cambielas e intente el registro nuevamente'
            
        else:
            query_message = 'SUCESS, Perfil actualizado satisfactoriamente'
            
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
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        
        # add [excluded] filter param value
        q_params['filter_excluded'] = str(system_user.username)
        
        state = WorkerManager.filter_workers(q_params, response)
        
        # check query state
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Usuario no registrado'
        elif state == INTERNAL_ERROR:
            query_message = 'ERROR, Error de Lista, No pudimmos recuperar la lista de trabajadores por problemas tecnicos. Intetelo de nuevo'
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            
            # list values
            'object_list': response.get('object_list'),
            'filtered_username': response.get('filtered_username'),
            'filter': response.get('filter'),
            'list_filters': 'username date'
        }
        
        # renderize list view page
        return render(req, self.template_name, context)

#
##
### TEST'S MANAGEMENT VIEWS ###########################################################

class AddTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.create_test')
    
    def post(self, req:HttpRequest):
        
        q_params = copy_dict(req.POST)
        response = dict()
        query_message = ''
        
        ### Try to create a new test on DB ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.create_test(system_user, q_params, response)
        
        ### Check test creation state ###
        
        if state == DUPLICATED_TEST:
            query_message = 'ERROR, Analisis no creado, No se pudo crear el analisis porque el id ya esta siendo utilizado por otro en proceso. CAMBIELO E INTENTELO DE NUEVEO'
        
        elif state == INTERNAL_ERROR:
            query_message = 'ERROR, Analisis no creado, No se pudo crear el analisis por un ERROR interno. INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS, El nuevo analisis fue agregado'
        
        ### make HTTP Response ###
        
        # go back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message': query_message
        }))

##################################################

class ResolveTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.resolve_test')
    
    def post(self, req:HttpRequest, test_id):
        
        q_params = copy_dict(req.POST)
        response = dict()
        query_message = ''
        
        ### Try to update test associted to ID ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.update_test_by_id(system_user, test_id, q_params, response)
        
        ### Check test update state ###
        
        if state == INTERNAL_ERROR:
            query_message = 'ERROR, Resultado no actualizado, No se pudo actualizar el resultado por un ERROR interno, INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS, Analisis actualizado satisfactoriamente'
        
        ### make HTTP Response ###
        
        # go back to test list
        return redirect(reverse('tests')+'?'+urlencode({
            'query_message': query_message
        }))

##################################################

class NotifyTestView(PermissionRequiredMixin, View):
    permission_required = ('backend.notify_test')
    
    def get(self, req:HttpRequest, test_id):
        
        query_message = ''
        response = {}
        
        ### Try to notify test associted to ID ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.notify_test_by_id(system_user, test_id, response)
        
        ### Check test notification state ###
        
        if state == INTERNAL_ERROR:
            query_message = 'ERROR, Resultado no enviado, No se pudo enviar el analisis por un ERROR interno, INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS, El analisis fue enviado satisfactoriamente'
        
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
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        
        # add [filter_test_states] filter param value
        if not 'filter_test_states' in q_params:
            q_params['filter_test_states'] = 'waiting resolved'
        
        # get logged user profile
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.filter_tests(system_user, q_params, response)
        
        ### Check query state ###
        
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Paciente no registrado'
            
        elif state == INTERNAL_ERROR:
            query_message = 'ERROR, Lista no disponible, No pudo obtenerse la lista de analisis por un ERROR interno, INTENTELO DE NUEVO'
        
        ### Make HTTP Response ###
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            
            # list values
            'object_list': response.get('object_list'),
            'filtered_username': response.get('filtered_username'),
            'filter': response.get('filter'),
            'list_filters': 'ci date test_state test_type'
        }
        
        # renderize test list view
        return render(req, self.template_name, context)

### RESULTS MANAGEMENT VIEWS ##########################################################

class SupressResultView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_result')
    
    def get(self, req:HttpRequest, test_id):
        
        query_message = ''
        response = {'test': None}
        
        ### Try to notify test associted to ID ###
        
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.delete_test_by_id(system_user, test_id, response)
        
        ### Check test supression state ###
        
        if state == INTERNAL_ERROR:
            query_message = 'ERROR, No se pudo eliminar el analisis por un ERROR interno, INTENTELO DE NUEVEO'
        
        else:
            query_message = 'SUCCESS, Analisis eliminado satisfactoriamente'
        
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
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        
        # get logued patient profile
        system_patient = PatientManager.get_registred_patient_user(req.user)
        
        if not 'filter_range_first_date' in q_params:
            q_params['filter_range_first_date'] = system_patient.date_joined.date().strftime('%Y-%m-%d')
        
        # add [ci] filter param value
        q_params['filter_ci'] = system_patient.ci
        
        # add [states] filter param value
        q_params['filter_states'] = 'waithing resolved notified'
        
        # get logged user profile
        system_user = SystemUserManager.get_registred_system_user(req.user)
        state = TestManager.filter_tests(system_user, q_params, response)
        
        ### Check query state ###
        
        if state == INTERNAL_ERROR:
            query_message = 'ERROR, Lista de resultados no disponible, No pudimos obtener la lista de resultados por un ERROR interno, INTENTALO DE NUEVO'
        
        ### Make HTTP Response ###
        
        # define context values
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            
            # list values
            'object_list': response.get('object_list'),
            'filtered_username': response.get('filtered_username'),
            'filter': response.get('filter'),
            'list_filters': 'date test_state test_type patient_filter'
        
        }
        
        # renderize patient test list view page
        return render(req, self.template_name, context)


### RESULTS MANAGEMENT VIEWS ##########################################################


class SupressEventView(PermissionRequiredMixin, View):
    template_name = 'event_list.html'
    permission_required = ('backend.delete_event')
    
    def get(self, req, event_id):
        query_message = ''
        
        # delete log of DB model 
        if EventManager.supress_event_by_id(event_id):
            query_message = 'SUCESS, Event Log deleted'
        else:
            query_message = 'ERROR, Event Log not deleted'
        
        return redirect('/events/?'+urlencode({
            'query_message': query_message
        }))

class SupressSelectedEventsView(PermissionRequiredMixin, View):
    permission_required = ('backend.delete_event')
    
    def get(self, req):
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        
        # delete log of DB model 
        state = EventManager.delete_events(q_params, response)
        
        # check operation state
        if state == SUCCESS:
            query_message = 'SUCESS, Seleccion eliminada satisfactoriamente'
        else:
            query_message = 'ERROR, No se pudieron eliminar los eventos seleccionados'
        
        return redirect('/events/?'+urlencode({
            'query_message': query_message
        }))

# VISUAL ##############################################################################

class EventListView(PermissionRequiredMixin, ListView):
    
    query_message = ""
    template_name = 'event_list.html'
    permission_required = ('backend.view_event_list')
    
    def get(self, req:HttpRequest):
        
        q_params = copy_dict(req.GET)
        response = dict()
        query_message = q_params.get('query_message')
        
        # get loggued admin profile
        system_user = SystemUserManager.get_registred_system_user(req.user)
        
        ### Filter events from DB ###
        
        state = EventManager.filter_events(q_params, response)
        
        ### Check event fetch state ###
            
        if state == INTERNAL_ERROR:
            query_message = 'ERROR, Lista de Eventos no disponible, No se pudo acceder a los eventos del perfil por un ERROR interno, INTENTELO DE NUEVO'
        
        if state == UNREGISTRED_PROFILE:
            query_message = 'ERROR, Usuario no registrado'
            
        context = {
            'current_time': datetime.now,
            'query_message': query_message,
            'system_user': system_user,
            
            # list values
            'object_list': response.get('object_list'),
            'filtered_username': response.get('filtered_username'),
            'filter': response.get('filter'),
            'list_filters': 'username date event_type'
            
        }
        
        # renderize profile event list view page
        return render(req, self.template_name, context)
