
from django.db.models import *
from django.contrib.auth.models import *
from django.contrib.contenttypes.models import ContentType
import backend

###############################################################################

class SystemUser(User):
    
    ci = CharField(max_length=12, null=False)
    phone = CharField(max_length=11, null=True)
    age = IntegerField(null=False, default=0)
    sex = CharField(max_length=2, null=False, default='M')
    icon_path = CharField(max_length=128, null=False, default='default_profile.png')

class SystemUserManager:    
    
    def get_system_user(user : User):
        try:
            return SystemUser.objects.get(id=user.id)
        except SystemUser.DoesNotExist:
            return None

###############################################################################
###############################################################################
class Patient(SystemUser):
    blod_group = CharField(max_length=5, null=True)

class PatientManager:
    
    # check if an instance of user is a Patient
    def is_patient_user(user : User) -> bool :
        
        try:
            return Patient.objects.get(id=user.id) is not None
        except Patient.DoesNotExist:
            return False
    
    def get_patient_user(user : User):
        
        try:
            return Patient.objects.get(id=user.id)
        except Patient.DoesNotExist:
            return None
    
    def get_patient_user_by_id(uid : int):
        
        try:
            return Patient.objects.get(id=uid)
        except Patient.DoesNotExist:
            return None
    
    def list_all():
        return Patient.objects.values()

    def create_patient_user(params):
        
        # create new patient relation with params fields values
        new_patient = Patient.objects.create_user(
            username = params.get('username'),
            password = params.get('password'),
            email = params.get('email'),
            ci = params.get('ci'),
            first_name = params.get('first_name'),
            last_name = params.get('last_name'),
            blod_group = params.get('blod_group_letter'),# + #params.get('blod_group_signus'),
            sex = params.get('sex'),
            age = params.get('age'),
            phone = params.get('phone'),
        )
        
        # define patient permissions
        new_patient.user_permissions.add(
            Permission.objects.get(codename='view_patient'),
            Permission.objects.get(codename='change_patient')
        )
        
        # store patient on DB
        new_patient.save()

        return new_patient
    
    def update_patient_user(edited_patient, q_params):
        
        # update patient with new params fields values
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
        
        # store updated patient on DB 
        edited_patient.save()
        
        return None
    
###############################################################################
    
class Worker(SystemUser):
    role = CharField(max_length=50, null=False, default='worker')
    
class WorkerManager:
    
    # check if an instance of user is a Worker
    def is_worker_user(user : User) -> bool :
        
        try:
            return Worker.objects.get(id=user.id) is not None
        except Worker.DoesNotExist:
            return False
    
    def get_worker_user(user : User):
        
        try:
            return Worker.objects.get(id=user.id)
        except Worker.DoesNotExist:
            return None
    
    def get_worker_user_by_id(wid : int):
        
        try:
            return Worker.objects.get(id=wid)
        except Worker.DoesNotExist:
            return None
    
    def list_all():
        return Worker.objects.values()

    def add_worker_user(params):
        
        # create new worker relation with params fields values
        new_worker = Worker.objects.create_user(
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
            new_worker.is_superuser = True
        else:
            
            # define worker permissions
            new_worker.user_permissions.add(backend.view_worker)
            
            if params.get('permission_view') == 'yes':
                new_worker.user_permissions.add(backend.view_test)
            
            if params.get('permission_add') == 'yes':
                new_worker.user_permissions.add(backend.add_test)
            
            if params.get('permission_edit') == 'yes':
                new_worker.user_permissions.add(backend.edit_test)
            
            if params.get('permission_delete') == 'yes':
                new_worker.user_permissions.add(backend.delete_test)
        
        # store worker on DB
        new_worker.save()
        return new_worker
    
    def update_worker_user(edited_worker, q_params):
        
        # update worker with new param fields values
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
        # define super_user role
        if q_params['permission_root'] == 'true':
            edited_worker.is_superuser = True
        else:
            
            # define worker permissions
            if q_params.get('permission_root') == 'yes':
                edited_worker.is_superuser = True
            else:
                edited_worker.is_superuser = False
                
                # tests see
                if q_params.get('permission_view') == 'yes':
                    edited_worker.user_permissions.add(backend.view_test)
                else:
                    edited_worker.user_permissions.remove(backend.view_test)
                
                # tests addition
                if q_params.get('permission_add') == 'yes':
                    edited_worker.user_permissions.add(backend.add_test)
                else:
                    edited_worker.user_permissions.remove(backend.add_test)
                
                # tests edition
                if q_params.get('permission_edit') == 'yes':
                    edited_worker.user_permissions.add(backend.edit_test)
                else:
                    edited_worker.user_permissions.remove(backend.edit_test)
                
                # test deletion
                if q_params.get('permission_delete') == 'yes':
                    edited_worker.user_permissions.add(backend.delete_test)
                else:
                    edited_worker.user_permissions.remove(backend.delete_test)
            
        
        # store updated worker on DB
        edited_worker.save()
        
        return None
        

#Test management model class
class Test(Model):
    type = CharField(max_length=32, default='uncategorized')
    state = CharField(max_length=32, default='waiting')
    patientCI = CharField(max_length=12, default='00000000000')
    testID = CharField(max_length=12, null=False, default="0000")
    result = CharField(max_length=256, null=True)
    begin_date = DateField(null=False, auto_now=True)
    resolution_date = DateField(null=True)

class TestManager:    
    
    def get_test(id:str):

        try:
            return Test.objects.get(testID = id)
        except Test.DoesNotExist:
            print('Not exists')
            return None
        except Test.MultipleObjectsReturned:
            print('Multiplied')
            return None
    
    def list_all():
        return Test.objects.values()
    

###############################################################################

#Event management model class
class SystemEvent(Model):
    date = DateField(null=False, auto_now=True)
    type = CharField(max_length=32, null=False, default="NOTICE")
    message = CharField(max_length=512, null=False, default="event")
    
class UserEvent(SystemEvent):
    user = ForeignKey(User, on_delete=CASCADE)
    
class EventManager:    
    
    def list_all_events():
        return SystemEvent.objects.values()
        
    def list_all_user_events():
        return UserEvent.objects.values()

    # check if an instance of event is a UserEvent
    def is_user_event(user : User) -> bool :
        return UserEvent.objects.get(id=user.id) is not None
    
    