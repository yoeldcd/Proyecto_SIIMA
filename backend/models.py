
from django.db.models import *;
from django.contrib.auth.models import *;

# Create your models here.
###############################################################################

class SystemUser(User):
    ci = CharField(max_length=11, null=False)
    phone = CharField(max_length=10, null=True)
    age = IntegerField(null=False)
    sex = CharField(max_length=1, null=False, default='M')
    icon_path = CharField(max_length=128, null=False, default='default_profile.png')
    
class SystemUserManager:    
    
    def get_system_user(user : User):
        try:
            return SystemUser.objects.get(id=user.id)
        except SystemUser.DoesNotExist:
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
    
    def list_all():
        return Worker.objects.values()

###############################################################################
class Patient(SystemUser):
    blod_group = CharField(max_length=3, null=True)

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
    
    def list_all():
        return Patient.objects.values()

###############################################################################

#Test management model class
class Test(Model):
    type = CharField(max_length=32, default='uncategorized')
    state = CharField(max_length=32, default='waiting')
    patientCI = CharField(max_length=11, default='00000000000')
    testID = CharField(max_length=11, null=False, default="0000")
    result = CharField(max_length=256, null=True)
    begin_date = DateField(null=False, auto_now=True)
    resolution_date = DateField(null=True)

class TestManager:    
    
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
    
    