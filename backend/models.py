
from django.db.models import *
from django.contrib.auth.models import *
from django.contrib.auth import authenticate, login
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

###############################################################################

class SystemUser(User):
    
    ci = CharField(max_length=12, null=False)
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
    
    def get_system_user(user : User):
        try:
            return SystemUser.objects.get(id=user.id)
        except SystemUser.DoesNotExist:
            return None
    
    def get_system_user_by_id(user_id):
        try:
            return SystemUser.objects.get(id=user_id)
        except SystemUser.DoesNotExist:
            return None

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
        
        # define patient permissions
        new_patient.user_permissions.add(
            Permission.objects.get(codename='view_patient_profile'),
            Permission.objects.get(codename='change_patient_profile'),
            Permission.objects.get(codename='delete_patient_profile'),
            Permission.objects.get(codename='view_result_list'),
            Permission.objects.get(codename='view_result'),
            Permission.objects.get(codename='delete_result')
        )
        
        log_message = f'CREATED: New Patient {new_patient}'
        
        # store patient on DB
        new_patient.save()
        print(log_message)

        return new_patient
    
    def update_patient_user(edited_patient, q_params):
        
        # update patient with new params fields values
        field = 'username'
        if q_params.get(field) != '':
            edited_patient.username = str(q_params.get(field))
        
        need_reauthenticate = False
        field = 'password'
        if q_params.get(field) != '':
            if edited_patient.is_authenticated:
                need_reauthenticate = True
            
            edited_patient.set_password(str(q_params.get(field)))
        
        

        field = 'email'
        if q_params.get(field) != '':
            edited_patient.email = str(q_params.get(field))
        
        field = 'ci'
        if q_params.get(field) != '':
            edited_patient.ci = str(q_params.get(field))
        
        field = 'first_name'
        if q_params.get(field) != '':
            edited_patient.first_name = str(q_params.get(field))
            
        field = 'last_name'
        if q_params.get(field) != '':
            edited_patient.last_name = str(q_params.get(field))
            
        field = 'sex'
        if q_params.get(field) != '':
            edited_patient.sex = str(q_params.get(field))
            
        field = 'age'
        if q_params.get(field) != '':
            edited_patient.age = int(q_params.get(field))
        
        field = 'phone'
        if q_params.get(field) != '':
            edited_patient.phone = str(q_params.get(field))
        
        field = 'blod_group'
        if q_params.get('blod_group_letter') != '' and q_params.get('blod_group_signus') != '':
            blod_group = str(q_params.get('blod_group_letter')) + str(q_params.get('blod_group_signus'))
            edited_patient.blod_group = blod_group
        
        log_message = f'UPDATED: Patient { edited_patient.id }'
        
        # store updated patient on DB 
        edited_patient.save()
        print(log_message)
        
        if need_reauthenticate:
            authenticate(username=edited_patient.username, password=q_params.get('password'))
        
        return None
    
    def supress_patient_user(supressed_patient):
        supressed_patient.delete()
        return None
    
###############################################################################
    
class Worker(SystemUser):
    role = CharField(max_length=50, null=False, default='worker')
    actions = CharField(max_length=22, null=False, default="None")
    
    def __str__(self):
        return '{'+super().__str__()+f'role: { self.role },\nactions: { self.actions }'+'}'

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
    
    def create_worker_user(params):
        
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
        
        # (grant or not) super_user role
        if params.get('permission_root') == 'true':
            new_worker.system_role = 'admin'
            new_worker.is_superuser = True
            actions += "-root"

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
        log_message = f'CREATED: Worker {new_worker}'
           
        # store worker on DB
        new_worker.save()
        print(log_message)
        
        return new_worker
    
    def update_worker_user(edited_worker, q_params, can_revoke):
        
        # update worker with new param fields values
        field = 'username'
        if field in q_params and q_params.get(field) != '':
            edited_worker.username = str(q_params.get(field))
        
        need_reauthenticate = False
        field = 'password'
        if field in q_params and q_params.get(field) != '':
            if edited_worker.is_authenticated:
                need_reauthenticate = True
                
            edited_worker.set_password(str(q_params.get(field)))
                
        field = 'email'
        if field in q_params and q_params.get(field) != '':
            edited_worker.email = str(q_params.get(field))
        
        field = 'ci'
        if field in q_params and q_params.get(field) != '':
            edited_worker.ci = str(q_params.get(field))
        
        field = 'first_name'
        if field in q_params and q_params.get(field) != '':
            edited_worker.first_name = str(q_params.get(field))
            
        field = 'last_name'
        if field in q_params and q_params.get(field) != '':
            edited_worker.last_name = str(q_params.get(field))
            
        field = 'sex'
        if field in q_params and q_params.get(field) != '':
            edited_worker.sex = str(q_params.get(field))
            
        field = 'age'
        if field in q_params and q_params.get(field) != '':
            edited_worker.age = int(q_params.get(field))
        
        field = 'phone'
        if field in q_params and q_params.get(field) != '':
            edited_worker.phone = str(q_params.get(field))
        
        field = 'role'
        if field in q_params and q_params.get(field) != '':
            edited_worker.role = str(q_params.get(field))
        
        # get and store all permission references on a dict
        permissions = Permission.objects        
        actions = ''
        
        print(q_params)
        
        # update permission
        if can_revoke:
            if q_params.get('permission_root') == 'yes':
                
                # grant super_user role permissions
                edited_worker.is_superuser = True
                edited_worker.system_role = 'admin'
                actions = "-root"
                
                edited_worker.user_permissions.add(permissions.get(codename='view_worker_list'))
                edited_worker.user_permissions.add(permissions.get(codename='delete_worker_profile'))
                
                edited_worker.user_permissions.add(permissions.get(codename='view_patient_list'))
                edited_worker.user_permissions.add(permissions.get(codename='change_patient_profile'))
                edited_worker.user_permissions.add(permissions.get(codename='delete_patient_profile'))
                
                edited_worker.user_permissions.add(permissions.get(codename='view_event_list'))
                edited_worker.user_permissions.add(permissions.get(codename='view_event'))
                edited_worker.user_permissions.add(permissions.get(codename='delete_event'))   
            else:
                # revoke super_user role role permissions
                edited_worker.is_superuser = False
                edited_worker.system_role = 'worker'
                
                edited_worker.user_permissions.remove(permissions.get(codename='view_worker_list'))
                edited_worker.user_permissions.remove(permissions.get(codename='delete_worker_profile'))
                edited_worker.user_permissions.remove(permissions.get(codename='view_patient_list'))
                
                edited_worker.user_permissions.remove(permissions.get(codename='change_patient_profile'))
                edited_worker.user_permissions.remove(permissions.get(codename='delete_patient_profile'))
                
                edited_worker.user_permissions.remove(permissions.get(codename='view_event_list'))
                edited_worker.user_permissions.remove(permissions.get(codename='view_event'))
                edited_worker.user_permissions.remove(permissions.get(codename='delete_event'))
            
            if edited_worker.system_role == 'worker':
                # define worker permissions

                if 'permission_view' in q_params: 
                    # (grant or revoke)  permission to access the tests list
                    if q_params.get('permission_view') == 'yes':
                        edited_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                        actions += '-v '
                    else:
                        edited_worker.user_permissions.remove(permissions.get(codename='view_test_list'))
                # (grant or revoke) permission to add a test
                if 'permission_create' in q_params and q_params.get('permission_create') == 'yes':
                    edited_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                    edited_worker.user_permissions.add(permissions.get(codename='create_test'))
                    actions += '-c '
                else:
                    edited_worker.user_permissions.remove(permissions.get(codename='create_test'))

                
                # (grant or revoke)  permission to resolve a test
                if 'permission_resolve' in q_params and q_params.get('permission_resolve') == 'yes':
                    edited_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                    edited_worker.user_permissions.add(permissions.get(codename='resolve_test'))
                    actions += '-r '
                else:
                    edited_worker.user_permissions.remove(permissions.get(codename='resolve_test'))

                # (grant or revoke)  permission to notify a test
                if 'permission_notify' in q_params and q_params.get('permission_notify') == 'yes':
                    edited_worker.user_permissions.add(permissions.get(codename='view_test_list'))
                    edited_worker.user_permissions.add(permissions.get(codename='notify_test'))
                    actions += '-n '
                else:
                    edited_worker.user_permissions.remove(permissions.get(codename='notify_test'))

            edited_worker.actions = actions
        
        log_message = f'UPDATED: Worker { edited_worker }'
        
        # store updated worker on DB
        edited_worker.save()
        print(log_message)

        if need_reauthenticate:
            authenticate(username=edited_worker.username, password=q_params.get('password'))
        
        return None
    
    def supress_worker_user(supressed_worker):
        supressed_worker.delete()
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
    
    def get_test_by_id(id:str):

        try:
            return Test.objects.get(id = id)
        except Test.DoesNotExist:
            print('Not exists')
            return None
        except Test.MultipleObjectsReturned:
            print('Multiplied')
            return None
    
    def list_all_unnotified_tests():
        return Test.objects.filter(~Q(state = 'notified')).values()
    
    def list_all_patient_tests(patient:Patient):
        return Test.objects.filter(patientCI = patient.ci).values()
    
    def add_test(params):
        
        # create a new test relation on DB
        Test.objects.create(
            patientCI = params.get('ci'),
            testID = params.get('id'),
            type = params.get('type'),
            begin_date = datetime.now
        ).save()
        
        return None
    
    def resolve_test(resolved_test:Test, result):
        
        # store test result on DB
        resolved_test.state = 'resolved'
        resolved_test.result = result
        resolved_test.resolution_date = datetime.now()
        resolved_test.save()                
        
        return None
    
    def notify_test(notified_test:Test):
        
        # store test result on DB
        notified_test.state = 'notified'
        notified_test.save()                
        
        return None

    def delete_test(notified_test:Test):
        
        # store test result on DB
        notified_test.delete()                
        
        return None
    

###############################################################################

#Event management model class
class SystemEvent(Model):
    date = DateTimeField(null=False, auto_now=True)
    type = CharField(max_length=32, null=False, default="normal")
    title = CharField(max_length=120, null=False, default="title")
    message = CharField(max_length=512, null=False, default="event")
    
class UserEvent(SystemEvent):
    user = ForeignKey(User, on_delete=CASCADE)
    
class EventManager:    
    
    def list_all_events():
        return SystemEvent.objects.all().order_by('-date').values()
        
    def list_all_user_events(user):
        return UserEvent.objects.filter(user = user).order_by('-date').values()
    
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
    
    def supress_event_by_id(event_id):
        
        try:
            SystemEvent.objects.get(id=event_id).delete()
            return True
        except SystemEvent.DoesNotExist:
            return False


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
    
    ################################

    """
    for perm in Permission.objects.all().order_by('-id').values_list():
        print(str(perm)+'\n')
    """