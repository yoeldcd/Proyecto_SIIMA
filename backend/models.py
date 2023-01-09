
from django.db import *
from django.db.models import *
from django.http import HttpRequest
from django.contrib.auth.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

###############################################################################
    
# State code values
INTERNAL_ERROR = -100
UNREGSTRED_EVENT = -30
UNREGISTRED_TEST = -21
DUPLICATED_TEST = -20
UNREGISTRED_PROFILE = -11
DUPLICATED_PROFILE = -10
INVALID_CREDENTIAL = -7
INVALID_PROFILE_DATA = -2
NOT_AUTENTICATED = -1

ERROR = 0
SUCCESS = 279

class SystemUser(User):
    
    ci = CharField(max_length=12, null=False, unique=True)
    phone = CharField(max_length=11, null=True)
    age = IntegerField(null=False, default=0)
    sex = CharField(max_length=2, null=False, default='M')
    icon_path = CharField(max_length=128, null=False, default='default_profile.png')
    system_role = CharField(max_length=128, null=False, default='patient')
    
    def __str__(self):
        text = f"""
            system_role: {self.system_role},
            
            id: { self.id },
            username: {self.username},
            password: {self.password},
            first_name: {self.first_name}
            last_name: {self.last_name},
            email: {self.email},
            last_login: {self.last_login},
            date_joined: {self.date_joined},
        
            ci: {self.ci},
            phone: {self.phone},
            age: {self.age},
            sex: {self.sex},
            icon_path: {self.icon_path},
            
        """
        if self.is_superuser:
            text += f"is_superuesr: true, "
        
        # list any permissions
        for perm in self.get_user_permissions():
            text += f"has_permission_{perm}: true,\n"
        
        return text

class SystemUserManager:    
    
    def filter_users(q_params:dict, response:dict):
        
        object_list = None
        sql_query = None
        filter = dict()
        
        # set default query params values
        system_roles = ""
        username = ""
        excluded = ""
        first_date = '1999-01-01'
        last_date = datetime.strftime(datetime.now(),'%Y-%m-%d')
        
        ## get filter params values
        if 'filter_system_roles' in q_params:
            system_roles = str(q_params.get('filter_system_roles') or "")
        
        if 'filter_username' in q_params:
            username = str(q_params.get('filter_username') or "")
        
        if 'filter_range_first_date' in q_params:
            first_date = str(q_params.get('filter_range_first_date') or "")
        
        if 'filter_range_last_date' in q_params:
            last_date = str(q_params.get('filter_range_last_date') or "")
        
        if 'filter_excluded' in q_params:
            excluded = q_params.get('filter_excluded')
            excluded = excluded.split(' ')
        
        # define response filter values
        filter['system_roles'] = system_roles
        filter['username'] = username
        filter['range_first_date'] = first_date
        filter['range_last_date'] = last_date
        response['filter'] = filter
        
        ## start DB query pipeline
        try:
            
            sql_query = SystemUser.objects.all()
            
            # filter user by system_role
            if not 'patient' in system_roles:
                sql_query = sql_query.exclude(system_role='patient')
            if not 'worker' in system_roles:
                sql_query = sql_query.exclude(system_role='worker')
            if not 'admin' in system_roles:
                sql_query = sql_query.exclude(system_role='admin')
            
            # filter user using math usernames
            if username != '':
                sql_query  = sql_query.filter(username__contains=username)
            
            # filter using excluded usernames
            if excluded != "":
                sql_query = sql_query.exclude(username__in=excluded)
            
            # filter user by last loguin
            if first_date != '':
                
                # normalize range filter
                if last_date == '':
                    last_date = first_date
                
                # format q_params str on date object
                t_first_date = datetime.strptime(first_date,'%Y-%m-%d')
                t_last_date = datetime.strptime(last_date,'%Y-%m-%d')
                
                sql_query = sql_query.filter(last_login__date__range=(t_first_date, t_last_date))
            
            # order and get users
            sql_query = sql_query.order_by('first_name')
            object_list = sql_query.values()
            
            # define query response values
            response['object_list'] = object_list
            response['filtered_username'] = username
            
        except InternalError:
            return INTERNAL_ERROR
        
        return SUCCESS
    
    def get_registred_system_user(user:User):
        
        if user is None:
            return None
        else:
            return SystemUser.objects.get(id=user.id)
        
    def get_system_user_by_id(user_id:int, response:dict):
        try:
            response['system_user'] = SystemUser.objects.get(id=user_id)
            return SUCCESS
        except SystemUser.DoesNotExist:
            return UNREGISTRED_PROFILE
    
    def authenticate_user(req:HttpRequest, params:dict, response:dict):
        username = params.get('username')
        password = params.get('password')
        existe_profile = False
        system_user = None
        
        try:
            # get profile asociated to username from DB
            system_user = SystemUser.objects.get(username=username)
            existe_profile = True
        except:
            EventManager.warning(None, 'AUTHENTICATION FAIL',f'Not registred user {username} intento iniciar sesion con password {password}')
            return UNREGISTRED_PROFILE
            
        # authenticate profile
        auth_user = authenticate(username=username, password=password)
        
        # check profile authentication
        if auth_user is None:
            EventManager.warning(None, 'AUTHENTICATION FAIL',f'User {username} intento iniciar sesion con password {password}')
            return INVALID_CREDENTIAL
        
        # login authenticated user    
        login(req, auth_user)
        EventManager.log(system_user, 'AUTHENTICATION',f'User {system_user.username} con rol {system_user.system_role} inicio sesion')
        
        response['system_user'] = system_user
        return SUCCESS
    
    def deauthenticate_user(req:HttpRequest):
        # finish current user sesion
        EventManager.log(req.user,'USER LOGGOUT',f'User {req.user.username} cerro su sesion ')    
        logout(req)

###############################################################################
class Patient(SystemUser):
    blod_group = CharField(max_length=5, null=True)
    
    def __str__(self):
        return '{'+super().__str__()+f'blod_group: { self.blod_group }'+'}'

class PatientManager:
    
    # check if an instance of user is a Patient
    def is_patient_user(user : User) -> bool :
        
        try:
            return Patient.objects.get(id=user.id) is not None
        except Patient.DoesNotExist:
            return False
    
    def filter_patients(q_params:dict, response:dict):
        
        # add role filter param
        q_params['filter_system_roles'] = 'patient'
        
        return SystemUserManager.filter_users(q_params, response)
        
    def get_registred_patient_user(user:User):
        return Patient.objects.get(id=user.id)
    
    def create_patient_user(system_user:SystemUser, params:dict, response:dict):
        
        try:
            # create new patient relation with params fields values
            new_patient = Patient.objects.create_user(
                
                username = str(params.get('username')),
                password = str(params.get('password')),
                email = str(params.get('email')),
                system_role = 'patient',
                
                ci = str(params.get('ci')),
                first_name = str(params.get('first_name')),
                last_name = str(params.get('last_name')),
                sex = str(params.get('sex')),
                age = str(params.get('age')),
                phone = str(params.get('phone')),
                blod_group = str(params.get('blod_group_letter')) + str(params.get('blod_group_signus')),
                
            )
        except IntegrityError:
            return DUPLICATED_PROFILE
        except InternalError:
            EventManager.error(system_user, "PROFILE INTERNAL ERROR", "Un error interno impidio la creacion de un perfil")
            return INTERNAL_ERROR
        
        # define patient profile permissions
        new_patient.user_permissions.add(
            Permission.objects.get(codename='view_patient_profile'),
            Permission.objects.get(codename='change_patient_profile'),
            Permission.objects.get(codename='delete_patient_profile'),
            Permission.objects.get(codename='view_result_list'),
            Permission.objects.get(codename='view_result'),
            Permission.objects.get(codename='delete_result')
        )
        
        # store patient on DB
        new_patient.save()
        
        # LOG ACTION
        if system_user is not None:
            EventManager.log(system_user, 'PATIENT PROFILE CREATED', f'El perfil del paciente {new_patient.username} fue creado por {system_user.username}')
        else:
            EventManager.log(new_patient, 'PATIENT PROFILE CREATED', f'El paciente {new_patient.username} creo su perfil')
        
        # response new profile
        response['patient'] = new_patient
        return SUCCESS
    
    def get_patient_user_by_id(patient_id:int, response:dict):
        
        try:
            # get patient asociate to ID from DB
            response['patient'] = Patient.objects.get(id=patient_id)
            return SUCCESS
        except Patient.DoesNotExist:
            return UNREGISTRED_PROFILE
    
    def update_patient_user_by_id(req:HttpRequest, system_user:SystemUser, patientID:int, q_params:dict, response:dict):
        changed_credentials = False
        
        try:
            # get updated patient asociate to ID from DB
            updated_patient = Patient.objects.get(id=patientID)
        except Patient.DoesNotExist:
            return UNREGISTRED_PROFILE
        except InternalError:
            EventManager.error(system_user, "PROFILE INTERNAL ERROR", "Un error interno impidio la actualizacion de un perfil")
            return INTERNAL_ERROR
        
        ### update patient with new params fields values ##
        
        field = 'username'
        if q_params.get(field) != '':
            updated_patient.username = str(q_params.get(field))
        
        need_reauthenticate = False
        field = 'password'
        if q_params.get(field) != '':
            changed_credentials = True
            updated_patient.set_password(str(q_params.get(field)))
        
        field = 'email'
        if q_params.get(field) != '':
            updated_patient.email = str(q_params.get(field))
        
        field = 'ci'
        if q_params.get(field) != '':
            updated_patient.ci = str(q_params.get(field))
        
        field = 'first_name'
        if q_params.get(field) != '':
            updated_patient.first_name = str(q_params.get(field))
            
        field = 'last_name'
        if q_params.get(field) != '':
            updated_patient.last_name = str(q_params.get(field))
            
        field = 'sex'
        if q_params.get(field) != '':
            updated_patient.sex = str(q_params.get(field))
            
        field = 'age'
        if q_params.get(field) != '':
            updated_patient.age = int(q_params.get(field))
        
        field = 'phone'
        if q_params.get(field) != '':
            updated_patient.phone = str(q_params.get(field))
        
        field = 'blod_group'
        if q_params.get('blod_group_letter') != '' and q_params.get('blod_group_signus') != '':
            blod_group = str(q_params.get('blod_group_letter')) + str(q_params.get('blod_group_signus'))
            updated_patient.blod_group = blod_group
        
        try:
            # store updated patient on DB 
            updated_patient.save()
        except IntegrityError:
            return DUPLICATED_PROFILE
        
        # reauthenticate
        if changed_credentials & updated_patient.id == system_user.id:
            login(req, authenticate(update_last_login, q_params['password']))
        
        # LOG ACTION
        EventManager.log(system_user, 'PATIENT PROFILE UPDATED', f'El perfil del paciente {updated_patient.username} fue modificado por {system_user.username}')
        
        response['patient'] = updated_patient
        return SUCCESS
    
    def supress_patient_user_by_id(system_user:SystemUser, patientID:int, q_parms:dict, response:dict):
        supressed_patient = None
        
        try:
            # get supressed patient asociate to ID from DB
            supressed_patient = Patient.objects.get(id=patientID)
            supressed_patient.delete()
            response['patient'] = supressed_patient
            
        except Patient.DoesNotExist:
            return UNREGISTRED_PROFILE
        except InternalError:
            EventManager.error(system_user, "PROFILE INTERNAL ERROR", "Un error interno impidio la supresion de un perfil")
            return INTERNAL_ERROR
        
        # LOG ACTION
        EventManager.warning(system_user, 'PATIENT PROFILE SUPRESSED', f'El perfil del paciente {supressed_patient.username} fue suprimido por {system_user.username}')
        
        return SUCCESS
    
###############################################################################
    
class Worker(SystemUser):
    role = CharField(max_length=50, null=False, default='worker')
    actions = CharField(max_length=22, null=False, default="None")
    
    def __str__(self):
        return '{'+super().__str__()+f'role: { self.role },\nactions: { self.actions }'+'}'

class WorkerManager:
    
    # check if an instance of user is a Worker
    def is_worker_user(user:User):
        
        try:
            return Worker.objects.get(id=user.id) is not None
        except Worker.DoesNotExist:
            return False
    
    def filter_workers(q_params:dict, response:dict):
        
        # add role filter param
        q_params['filter_system_roles'] = 'worker admin'
        
        return SystemUserManager.filter_users(q_params, response)
    
    def get_registred_worker_user(user:User):
        return Worker.objects.get(id=user.id)
    
    def create_worker_user(system_user:SystemUser, params:dict, response:dict):
        
        try:
            # create new worker relation with params fields values
            new_worker = Worker.objects.create_user(
                username = str(params.get('username')),
                password = str(params.get('password')),
                email = str(params.get('email')),
                system_role = 'worker',

                ci = str(params.get('ci')),
                first_name = str(params.get('first_name')),
                last_name = str(params.get('last_name')),
                sex = str(params.get('sex')),
                age = str(params.get('age')),
                phone = str(params.get('phone')),
                role = str(params.get('role'))
            )
        except IntegrityError:
            return DUPLICATED_PROFILE
        except InternalError:
            EventManager.error(system_user, "PROFILE INTERNAL ERROR", "Un error interno impidio la creacion de un perfil")
            return INTERNAL_ERROR
        
        # (grant or not) super_user role
        if params.get('permission_root') == 'true':
            new_worker.system_role = 'admin'
            new_worker.is_superuser = True
            new_worker.actions ="-root" 
        
        else:
            # get and store all permission references on a dict
            permissions = Permission.objects
            actions = ""
            
            # define worker permissions
            new_worker.user_permissions.add(permissions.get(codename='view_worker_profile'))
            new_worker.user_permissions.add(permissions.get(codename='change_worker_profile'))
            
            # (grant or not) view permission
            if params.get('permission_view') == 'yes':
                new_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                actions += "-v "
            
            # (grant or not) add permission
            if params.get('permission_create') == 'yes':
                new_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                new_worker.user_permissions.add(permissions.get(codename='create_test'))
                actions += "-c "
            
            # (grant or not) edit permission
            if params.get('permission_resolve') == 'yes':
                new_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                new_worker.user_permissions.add(permissions.get(codename='resolve_test'))
                actions += "-r "
            
            # (grant or not) supress permission
            if params.get('permission_notify') == 'yes':
                new_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                new_worker.user_permissions.add(permissions.get(codename='notify_test'))
                actions += "-n "
            
            new_worker.actions = actions 
        
        try:
            # store worker on DB
            new_worker.save()
        except IntegrityError:
            return DUPLICATED_PROFILE
        
        # LOG ACTION
        EventManager.log(system_user, 'WORKER PROFILE CREATED', f'El perfil del trabajador {new_worker.username} fue creado por {system_user.username}')
        
        response['worker'] = new_worker
        return SUCCESS
    
    def get_worker_user_by_id(worker_id:int, response:dict):
        
        try:
            # get worker asociated to ID from DB
            response['worker'] = Worker.objects.get(id=worker_id)
            return SUCCESS
        except Worker.DoesNotExist:
            return UNREGISTRED_PROFILE
        except IntegrityError:
            return DUPLICATED_PROFILE
        
    def update_worker_user_by_id(req:HttpRequest, system_user:SystemUser, worker_id:int, q_params:dict, response:dict):
        changed_credentials = False
        
        try:
            # get updated worker asociated to ID from DB
            updated_worker = Worker.objects.get(id=worker_id) 
        except Worker.DoesNotExist:
            return UNREGISTRED_PROFILE
        except InternalError:
            EventManager.error(system_user, "PROFILE INTERNAL ERROR", "Un error interno impidio la actualizacion de un perfil")
            return INTERNAL_ERROR
        
        # update worker with new param fields values
        field = 'username'
        if field in q_params and q_params.get(field) != '':
            updated_worker.username = str(q_params.get(field))
        
        field = 'password'
        if field in q_params and q_params.get(field) != '':
            changed_credentials = True
            updated_worker.set_password(str(q_params.get(field)))
        
        field = 'email'
        if field in q_params and q_params.get(field) != '':
            updated_worker.email = str(q_params.get(field))
        
        field = 'ci'
        if field in q_params and q_params.get(field) != '':
            updated_worker.ci = str(q_params.get(field))
        
        field = 'first_name'
        if field in q_params and q_params.get(field) != '':
            updated_worker.first_name = str(q_params.get(field))
            
        field = 'last_name'
        if field in q_params and q_params.get(field) != '':
            updated_worker.last_name = str(q_params.get(field))
            
        field = 'sex'
        if field in q_params and q_params.get(field) != '':
            updated_worker.sex = str(q_params.get(field))
            
        field = 'age'
        if field in q_params and q_params.get(field) != '':
            updated_worker.age = int(q_params.get(field))
        
        field = 'phone'
        if field in q_params and q_params.get(field) != '':
            updated_worker.phone = str(q_params.get(field))
        
        field = 'role'
        if field in q_params and q_params.get(field) != '':
            updated_worker.role = str(q_params.get(field))
        
        # check if user can (ROVOKE OR GRANT) permission it' self
        if system_user.system_role == 'admin' and system_user.id != updated_worker.id:
            
            # get and store all permission references on a dict
            permissions = Permission.objects        
            
            if q_params.get('permission_root') == 'yes':
                
                # grant super_user role
                updated_worker.is_superuser = True
                updated_worker.system_role = 'admin'
                updated_worker.actions = '-root-'
                
                # grant super_user role permissions
                updated_worker.user_permissions.add(permissions.get(codename='view_worker_list'))
                updated_worker.user_permissions.add(permissions.get(codename='delete_worker_profile'))
                
                updated_worker.user_permissions.add(permissions.get(codename='view_patient_list'))
                updated_worker.user_permissions.add(permissions.get(codename='change_patient_profile'))
                updated_worker.user_permissions.add(permissions.get(codename='delete_patient_profile'))
                
                updated_worker.user_permissions.add(permissions.get(codename='view_event_list'))
                updated_worker.user_permissions.add(permissions.get(codename='view_event'))
                updated_worker.user_permissions.add(permissions.get(codename='delete_event'))
                
            else:
                # revoke super_user role
                updated_worker.is_superuser = False
                updated_worker.system_role = 'worker'
                
                # revoke super_user permissions
                updated_worker.user_permissions.remove(permissions.get(codename='view_worker_list'))
                updated_worker.user_permissions.remove(permissions.get(codename='delete_worker_profile'))
                updated_worker.user_permissions.remove(permissions.get(codename='view_patient_list'))
                
                updated_worker.user_permissions.remove(permissions.get(codename='change_patient_profile'))
                updated_worker.user_permissions.remove(permissions.get(codename='delete_patient_profile'))
                
                updated_worker.user_permissions.remove(permissions.get(codename='view_event_list'))
                updated_worker.user_permissions.remove(permissions.get(codename='view_event'))
                updated_worker.user_permissions.remove(permissions.get(codename='delete_event'))
            
            if updated_worker.system_role == 'worker':
                # define worker role permissions
                actions = ''

                # (grant or revoke)  permission to access the tests list
                if 'permission_view' in q_params and q_params.get('permission_view') == 'yes':
                    updated_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                    actions += '-v '
                else:
                    updated_worker.user_permissions.remove(permissions.get(codename='view_test_list'))
                
                # (grant or revoke) permission to add a test
                if 'permission_create' in q_params and q_params.get('permission_create') == 'yes':
                    updated_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                    updated_worker.user_permissions.add(permissions.get(codename='create_test'))
                    actions += '-c '
                else:
                    updated_worker.user_permissions.remove(permissions.get(codename='create_test'))
                
                # (grant or revoke)  permission to resolve a test
                if 'permission_resolve' in q_params and q_params.get('permission_resolve') == 'yes':
                    updated_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                    updated_worker.user_permissions.add(permissions.get(codename='resolve_test'))
                    actions += '-r '
                else:
                    updated_worker.user_permissions.remove(permissions.get(codename='resolve_test'))
                
                # (grant or revoke)  permission to notify a test
                if 'permission_notify' in q_params and q_params.get('permission_notify') == 'yes':
                    updated_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                    updated_worker.user_permissions.add(permissions.get(codename='notify_test'))
                    actions += '-n '
                else:
                    updated_worker.user_permissions.remove(permissions.get(codename='notify_test'))
                
                #define worker role actions granteds
                updated_worker.actions = actions
                
        try:
            # store updated worker on DB
            updated_worker.save()
        except IntegrityError:
            return DUPLICATED_PROFILE
        
        # reauthenticate
        if changed_credentials & updated_worker.id == system_user.id:
            login(req, authenticate(update_last_login, q_params['password']))
        
        # LOG ACTION
        EventManager.log(system_user, 'WORKER PROFILE UPDATED', f'El perfil del trabajador {updated_worker.username} fue modificado por {system_user.username}')
        
        response['worker'] = updated_worker
        return SUCCESS
    
    def supress_worker_user_by_id(system_user:SystemUser, worker_id:int, q_params:dict, response:dict):
        supressed_worker = None
        
        try:
            # get supressed worker asociated to ID from DB
            supressed_worker = Worker.objects.get(id=worker_id)
            supressed_worker.delete()
            response['worker'] = supressed_worker
            
        except Worker.DoesNotExist:
            return UNREGISTRED_PROFILE
        except InternalError:
            EventManager.error(system_user, "PROFILE INTERNAL ERROR", "Un error interno impidio la eliminacion de un perfil")
            return INTERNAL_ERROR
        
        # LOG ACTION
        EventManager.warning(system_user,'WORKER PROFILE SUPRESSED', f'El perfil del trabajador {supressed_worker.username} fue suprimido por {system_user.username}')
        
        return SUCCESS    

#Test management model class
class Test(Model):
    type = CharField(max_length=32, default='uncategorized')
    state = CharField(max_length=32, default='waiting')
    patientCI = CharField(max_length=12, default='00000000000')
    testID = CharField(max_length=12, null=False, default="0000", unique=True)
    result = CharField(max_length=256, null=True)
    begin_date = DateField(null=False, auto_now=True)
    resolution_date = DateField(null=True)

class TestManager:    
    
    def get_test_by_id(id:str):

        try:
            return Test.objects.get(id = id)
        except Test.DoesNotExist:
            return UNREGISTRED_TEST
        except Test.MultipleObjectsReturned:
            return DUPLICATED_TEST
        except InternalError:
            EventManager.error(None, "TEST INTERNAL ERROR", "Un error interno impidio recuperacion de un analisis")
            return INTERNAL_ERROR
        
    def filter_tests(system_user:SystemUser, q_params:dict, response:dict):
        
        # response values
        detailed_patient = None
        object_list = None
        filter = dict()
        
        # set default query params values
        ci = None
        test_states = None
        test_types = None
        first_date = datetime.strftime(datetime.now(),'%Y-%m-%d')
        last_date = first_date
        
        # get filter params values
        if 'filter_ci' in q_params:
            ci = str(q_params.get('filter_ci') or "")
        
        if 'filter_range_first_date' in q_params:
            first_date = str(q_params.get('filter_range_first_date') or "")
        
        if 'filter_range_last_date' in q_params:
            last_date = str(q_params.get('filter_range_last_date') or "")
        
        if 'filter_test_states' in q_params:
            test_states = q_params.get('filter_test_states').split(' ')
        
        if 'filter_test_types' in q_params:
            test_types = q_params.get('filter_test_types').split(' ')
        
        # define response filter values
        filter['ci'] = ci
        filter['range_first_date'] = first_date
        filter['range_last_date'] = last_date
        filter['test_states'] = str(test_states)
        filter['test_types'] = str(test_types)
        
        response['filter'] = filter
        
        # start DB query pipeline
        try:
            
            sql_query = Test.objects.all()
            
            # filter test by patientCI
            if ci is not None:
                sql_query = sql_query.filter(patientCI = ci)
            
            # filter test by time range
            if first_date != '':
                
                # normalize filter
                if last_date == '':
                    last_date = first_date
                
                # format q_params str on date object
                t_first_date = datetime.strptime(first_date,'%Y-%m-%d')
                t_last_date = datetime.strptime(last_date,'%Y-%m-%d')
                
                sql_query = sql_query.filter(begin_date__range=(t_first_date, t_last_date))
            
            # filter test by states
            if test_states is not None:
                sql_query = sql_query.filter(state__in = test_states)
            
            # filter test by type
            if test_types is not None:
                sql_query = sql_query.filter(type__in = test_types)
            
            # order tests by date
            sql_query = sql_query.order_by('-begin_date')
            object_list = sql_query.values()
            
            # define query response values
            response['object_list'] = object_list
            
            # add profile data
            if detailed_patient is not None:
                response['filtered_username'] = detailed_patient.username
            
        except InternalError:
            EventManager.error(None, "TEST INTERNAL ERROR", "Un error interno impidio la recuperacion de la lista de analisis")
            return INTERNAL_ERROR
        
        return SUCCESS
        
    def create_test(system_user:SystemUser, params:dict, response:dict):
        
        try:
            # create new test on DB
            new_test = Test.objects.create(
                patientCI = params.get('ci'),
                testID = params.get('id'),
                type = params.get('type'),
                begin_date = datetime.now
            )
            response['test'] = new_test

            EventManager.log(system_user, "TEST CREATED", f"Se registro el nuevo analisis [{ new_test.id }]en la BD")
            
        except IntegrityError:
            return DUPLICATED_TEST
        except InternalError:
            EventManager.error(None, "TEST INTERNAL ERROR", "Un error interno impidio la creacion de un analisis")
            return INTERNAL_ERROR
        
        return SUCCESS
    
    def update_test_by_id(system_user:SystemUser, test_id:int, q_params:dict, response:dict):
        updated_test = None
        
        try:
            # get updated test associeted to ID
            updated_test = Test.objects.get(id=test_id)
            
            # store new test values on DB
            updated_test.state = 'resolved'
            updated_test.result = q_params['result']
            updated_test.resolution_date = datetime.now()
            updated_test.save()
            
            response['test'] = updated_test
            EventManager.log(system_user, "TEST UPDATED", f"Se registro el resultado del analisis [{updated_test.id}] en la BD ")
            
        except Test.DoesNotExist:
            return UNREGISTRED_TEST
        except InternalError:
            EventManager.error(None, "TEST INTERNAL ERROR", "Un error interno impidio la actualizacion de un analisis")
            return INTERNAL_ERROR
            
        
        
        return SUCCESS
    
    def notify_test_by_id(system_user:SystemUser, test_id:int, response:dict):
        
        try:
            # get updated test associeted to ID
            updated_test = Test.objects.get(id=test_id)
            
            # store new test state on DB
            updated_test.state = 'notified'
            updated_test.save()
            
            response['test'] = updated_test
            EventManager.log(system_user, "TEST NOTIFIED", f"Se envio el analisis [{updated_test.id}] hacia el usuario con CI: { updated_test.patientCI }")
            
        except Test.DoesNotExist:
            return UNREGISTRED_TEST
        
        except InternalError:
            EventManager.error(None, "TEST INTERNAL ERROR", "Un error interno impidio la notificacion de un analisis")
            return INTERNAL_ERROR
        
        return SUCCESS
    
    def delete_test_by_id(system_user:SystemUser, test_id:int, response:dict):
        
        try:
            # delete test associeted to ID
            supressed_test = Test.objects.get(id=test_id)
            supressed_test.delete()
            response['test'] = supressed_test    
            
            EventManager.log(system_user, "TEST SUPRESSED", f"El usuario [{system_user.id}] elimino el analisis [{supressed_test.id}]")
                
        except Test.DoesNotExist:
            return UNREGISTRED_TEST
        
        except InternalError:
            EventManager.error(None, "TEST INTERNAL ERROR", "Un error interno impidio la eliminacion de un analisis")
            return INTERNAL_ERROR
        
        return SUCCESS

###############################################################################

#Event management model class
class EventType:
    ERROR = 'danger'
    WARNING = 'warning'
    LOG = 'log'
    
class SystemEvent(Model):
    
    date = DateTimeField(null=False, auto_now=True)
    type = CharField(max_length=32, null=False, default="normal")
    title = CharField(max_length=120, null=False, default="title")
    message = CharField(max_length=512, null=False, default="event")
    
class UserEvent(SystemEvent):
    user = ForeignKey(User, on_delete=CASCADE)
    
class EventManager:
    
    def filter_events(q_params:dict, response:dict):
        
        object_list = None
        detailed_user = None
        sql_query = None
        filter = dict()
        
        # set default query params values
        id = ""
        username = ""
        event_type = None
        first_date = '1999-01-01'
        last_date = datetime.strftime(datetime.now(),'%Y-%m-%d')
        
        # get event filter params
        if 'filter_id' in q_params:
            id = str(q_params.get('filter_id') or "")
        
        if 'filter_username' in q_params:
            username = str(q_params.get('filter_username') or "")
        
        if 'filter_event_type' in q_params:
            event_type = str(q_params.get('filter_event_type') or "")
        
        if 'filter_range_first_date' in q_params:
            first_date = str(q_params.get('filter_range_first_date') or "")
        
        if 'filter_range_last_date' in q_params:
            last_date = str(q_params.get('filter_range_last_date') or "")
        
        # define response filter values
        filter['id'] = str(id)
        filter['username'] = str(username)
        filter['event_type'] = str(event_type)
        filter['range_first_date'] = str(first_date)
        filter['range_last_date'] = str(last_date)
        
        response['filter'] = filter
        
        # start DB query pipeline
        try:
            
            sql_query = SystemEvent.objects.all()
            
            # filter events by profile entry
            if id != '' or username != '':
                
                try:    
                    
                    # get user associted to credentials
                    if id != '':
                        detailed_user = SystemUser.objects.get(id=id)        
                    else:
                        detailed_user = SystemUser.objects.get(username=username)
                    
                    # filter all events of user profile
                    sql_query = UserEvent.objects.filter(user = detailed_user)
                
                except SystemUser.DoesNotExist:
                    return UNREGISTRED_PROFILE
                except InternalError:
                    return INTERNAL_ERROR
            
            
            # filter events by type
            if event_type != None:
                sql_query = UserEvent.objects.filter(type=event_type)
            
            
            # filter events by time range
            if first_date != '':
            
                # normalize date filter
                if last_date == '':
                    last_date = first_date
                
                # format q_params str on date object
                t_first_date = datetime.strptime(first_date,'%Y-%m-%d')
                t_last_date = datetime.strptime(last_date,'%Y-%m-%d')
                
                sql_query = sql_query.filter(date__date__range=(t_first_date, t_last_date))
            
            # order and get events from DB
            sql_query = sql_query.order_by('-date')
            object_list = sql_query.values()
            
            # define query response values
            response['object_list'] = object_list
            
            # add profile response data
            if detailed_user is not None:
                response['filtered_username'] = detailed_user.username
            
        except InternalError:
            return INTERNAL_ERROR
                        
        return SUCCESS
    
    # check if an instance of event is a UserEvent
    def is_user_event(event : SystemEvent) -> bool :
        return UserEvent.objects.get(id=event.id) is not None
    
    def log_system_event(type, title, message):
        
        SystemEvent.objects.create(
            type = str(type).lower(),
            title = str(title),
            message = str(message),
            date = datetime.now()
        )
    
    def log_user_event(user, type, title, message):
        
        UserEvent.objects.create(
            type = str(type).lower(),
            title = str(title),
            message = str(message),
            date = datetime.now(),
            user = user
        )

        return None
    
    def error(user, title, message):
        
        # Store one Error Event Log on DB    
        if user is None:
            EventManager.log_system_event(EventType.ERROR, title, message)
        else:
            EventManager.log_user_event(user, EventType.ERROR, title, message)
    
    def warning(user, title, message):
        
        # Store one Warning Event Log on DB
        if user is None:
            EventManager.log_system_event(EventType.WARNING, title, message)
        else:
            EventManager.log_user_event(user, EventType.WARNING, title, message)
    
    def log(user, title, message):
        
        # Store one Normal Event Log on DB
        if user is None:
            EventManager.log_system_event(EventType.LOG, title, message)
        else:
            EventManager.log_user_event(user, EventType.LOG, title, message)
    
    def supress_event_by_id(event_id):
        
        try:
            # remove event asociated to id from DB
            SystemEvent.objects.get(id=event_id).delete()
        
        except SystemEvent.DoesNotExist:
            return UNREGSTRED_EVENT
        
        return SUCCESS

# SYSTEM PEMISSIONS ##################################################################

def make_custom_permissions():
    systemuser_content_type = ContentType.objects.get_for_model(SystemUser)
    
    # WORKER ###################
    
    codename = 'view_worker_list'
    if Permission.objects.filter(codename=codename).count() == 0:
        Permission.objects.create(codename=codename, name="see list workers", content_type=systemuser_content_type)
    
    codename = 'view_worker_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
        Permission.objects.create(codename=codename, name="see worker properties", content_type=systemuser_content_type)
    
    codename = 'add_worker_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
        Permission.objects.create(codename=codename, name="create worker profile account", content_type=systemuser_content_type)
    
    codename = 'change_worker_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="edit worker profile account", content_type=systemuser_content_type)
    
    codename = 'delete_worker_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="delete worker profile account", content_type=systemuser_content_type)
    
    # PATIENT ###################
    
    codename = 'view_patient_list'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="see list patients", content_type=systemuser_content_type)
    
    codename = 'view_patient_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="see patient properties", content_type=systemuser_content_type)
    
    codename = 'add_patient_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="create patient profile account", content_type=systemuser_content_type)
    
    codename = 'change_patient_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="edit patient profile account", content_type=systemuser_content_type)
    
    codename = 'delete_patient_profile'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="delete patient profile account", content_type=systemuser_content_type)
    
    # TEST #####################
    
    codename = 'view_test_list'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="see list test", content_type=systemuser_content_type)
    
    codename = 'create_test'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="create new test", content_type=systemuser_content_type)
    
    codename = 'resolve_test'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="set test results", content_type=systemuser_content_type)
    
    codename = 'notify_test'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="notify test of list", content_type=systemuser_content_type)
    
    
    # RESULTS ######################
    
    codename = 'view_result_list'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="see list results", content_type=systemuser_content_type)
    
    codename = 'view_result'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="view result details", content_type=systemuser_content_type)
    
    codename = 'delete_result'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="delete result of list", content_type=systemuser_content_type)
    
    
    # EVENTS #######################
    
    codename = 'view_event_list'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="see list events", content_type=systemuser_content_type)
    
    codename = 'view_event'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="see event details", content_type=systemuser_content_type)
    
    codename = 'delete_event'
    if Permission.objects.filter(codename=codename).count() == 0:
       Permission.objects.create(codename=codename, name="see event details", content_type=systemuser_content_type)
    
# UTIL FUNCTIONS ################
    
# clone an unmutable dict into one mutable dict to modify query input's params
def copy_dict(dict1:dict):
    
    dict2 = dict()
    
    for k in dict1.keys():
        dict2[k] = dict1[k]
    
    return dict2
    